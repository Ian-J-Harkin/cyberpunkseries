"""
main.py — CLI entry point for the Narrative Physics Engine.

Commands:
  python main.py setup    — run the setup pipeline (once per project)
  python main.py write    — run the writing loop (once per scene)
  python main.py export   — export scenes to Markdown and store to JSON
  python main.py status   — print current engine store summary
  python main.py reset    — delete the DB and start fresh
"""

import os
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.rule import Rule
from rich.text import Text
from dotenv import load_dotenv

from state import (
    CharacterInput,
    RelationshipPairInput,
    SetupInput,
    SceneBriefInput,
)
from graphs import get_graphs
from persistence import (
    get_config,
    load_store_from_state,
    export_store_to_file,
    export_scenes_to_markdown,
    reset_store,
    DEFAULT_DB_PATH,
)

load_dotenv()

app = typer.Typer(help="Narrative Physics Engine — AI-assisted fiction pipeline")
console = Console()

ACT_POSITIONS = [
    "Act 1 — Establishing",
    "Act 1 — Inciting Incident",
    "Act 2 — Rising Pressure",
    "Act 2 — Midpoint",
    "Act 2 — Dark Night",
    "Act 3 — Climax",
    "Act 3 — Resolution",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_api_key():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print(
            "[bold red]Error:[/bold red] ANTHROPIC_API_KEY not set. "
            "Add it to your .env file or environment."
        )
        raise typer.Exit(1)


def print_header(title: str):
    console.print()
    console.print(Rule(f"[bold cyan]{title}[/bold cyan]"))
    console.print()


def prompt_characters() -> list[CharacterInput]:
    """Interactively collect character definitions."""
    console.print("[bold]Enter your characters.[/bold] "
                  "Format: Name | brief description")
    console.print("Press Enter on a blank line when done.\n")
    characters = []
    while True:
        line = Prompt.ask("  Character", default="").strip()
        if not line:
            if not characters:
                console.print("[yellow]You need at least one character.[/yellow]")
                continue
            break
        parts = [p.strip() for p in line.split("|", 1)]
        if len(parts) < 2:
            console.print("[yellow]Use format: Name | description[/yellow]")
            continue
        characters.append(CharacterInput(name=parts[0], description=parts[1]))
        console.print(f"  [green]✓[/green] {parts[0]}")
    return characters


def prompt_pairs(characters: list[CharacterInput]) -> list[RelationshipPairInput]:
    """Interactively collect relationship pairs."""
    names = [c.name for c in characters]
    console.print(
        f"\n[bold]Enter relationship pairs to map.[/bold] "
        f"Characters: {', '.join(names)}"
    )
    console.print("Format: Name A | Name B  — press Enter on blank line when done.\n")
    pairs = []
    while True:
        line = Prompt.ask("  Pair", default="").strip()
        if not line:
            break
        parts = [p.strip() for p in line.split("|", 1)]
        if len(parts) < 2:
            console.print("[yellow]Use format: Name A | Name B[/yellow]")
            continue
        pairs.append(RelationshipPairInput(char_a=parts[0], char_b=parts[1]))
        console.print(f"  [green]✓[/green] {parts[0]} ↔ {parts[1]}")
    return pairs


def prompt_act_position() -> str:
    """Let user pick act position from numbered list."""
    console.print("\n[bold]Act position:[/bold]")
    for i, pos in enumerate(ACT_POSITIONS, 1):
        console.print(f"  {i}. {pos}")
    while True:
        choice = Prompt.ask("\n  Enter number", default="1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(ACT_POSITIONS):
                return ACT_POSITIONS[idx]
        except ValueError:
            pass
        console.print("[yellow]Please enter a number from the list.[/yellow]")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@app.command()
def setup(db_path: str = typer.Option(DEFAULT_DB_PATH, help="Path to SQLite DB file")):
    """
    Run the setup pipeline. Generates Physics Document, Character State Machines,
    and Relationship Force Fields. Run once per project.
    """
    check_api_key()
    print_header("NARRATIVE PHYSICS ENGINE — SETUP")

    console.print("This will generate your Physics Document, Character State Machines,")
    console.print("and Relationship Force Fields. Run this once per project.\n")

    premise = Prompt.ask("[bold]Story premise[/bold] (2-3 sentences)")
    genre_tone = Prompt.ask("[bold]Genre and tone[/bold]")
    characters = prompt_characters()
    pairs = prompt_pairs(characters)

    setup_input = SetupInput(
        premise=premise,
        genre_tone=genre_tone,
        characters=characters,
        pairs=pairs,
    )

    console.print()
    console.print(Panel(
        f"[bold]Premise:[/bold] {premise}\n"
        f"[bold]Genre/Tone:[/bold] {genre_tone}\n"
        f"[bold]Characters:[/bold] {', '.join(c.name for c in characters)}\n"
        f"[bold]Pairs:[/bold] {', '.join(f'{p.char_a}/{p.char_b}' for p in pairs)}",
        title="Confirm Setup",
        border_style="cyan"
    ))

    if not Confirm.ask("\nProceed?", default=True):
        raise typer.Exit()

    setup_graph, _ = get_graphs(db_path)
    config = get_config()

    console.print("\n[cyan]Running setup pipeline...[/cyan]")
    console.print("  [dim]Stage 1: Generating Physics Document (Opus)[/dim]")

    initial_state = {"setup_input": setup_input}

    with console.status("[cyan]Generating — this takes a minute or two...[/cyan]"):
        final_state = setup_graph.invoke(initial_state, config=config)

    store = final_state.get("engine_store")
    if store and store.setup_complete:
        console.print()
        console.print(Panel(
            f"[green]✓[/green] Physics Document generated\n"
            f"[green]✓[/green] Character State Machines: "
            f"{', '.join(store.character_machines.keys())}\n"
            f"[green]✓[/green] Relationship Force Fields: "
            f"{', '.join(store.relationships.keys())}",
            title="[green]Setup Complete[/green]",
            border_style="green"
        ))
        console.print("\nYou can now run [bold]python main.py write[/bold] to write your first scene.")
    else:
        console.print("[red]Setup failed. Check your API key and try again.[/red]")


@app.command()
def write(db_path: str = typer.Option(DEFAULT_DB_PATH, help="Path to SQLite DB file")):
    """
    Run the writing loop for one scene. Drafts the scene and updates rolling state.
    """
    check_api_key()
    print_header("NARRATIVE PHYSICS ENGINE — WRITE SCENE")

    _, writing_graph = get_graphs(db_path)
    config = get_config()

    # Check store exists
    checkpoint = writing_graph.checkpointer.get(config)
    if not checkpoint:
        console.print("[red]No engine store found. Run[/red] [bold]python main.py setup[/bold] [red]first.[/red]")
        raise typer.Exit(1)

    store = load_store_from_state(checkpoint.get("channel_values", {}))
    scene_number = len(store.scene_history) + 1

    console.print(f"[dim]Project:[/dim] {store.premise[:80]}...")
    console.print(f"[dim]Scene:[/dim] #{scene_number}")
    console.print(f"[dim]Characters available:[/dim] {', '.join(store.character_machines.keys())}\n")

    # Collect scene brief
    chars_input = Prompt.ask("[bold]Characters in this scene[/bold] (comma separated)")
    characters_in_scene = [c.strip() for c in chars_input.split(",")]

    act_position = prompt_act_position()

    previous_summary = Prompt.ask(
        "\n[bold]What just happened[/bold] (previous scene summary, or 'opening scene')"
    )
    plot_function = Prompt.ask("[bold]What must happen in this scene[/bold]")
    new_state_goal = Prompt.ask("[bold]What must change by the end[/bold]")
    character_knowledge = Prompt.ask(
        "[bold]What does each character currently know[/bold] "
        "(critical for information economy)"
    )
    emotional_states = Prompt.ask(
        "[bold]Current emotional states[/bold] "
        "(reference palette names e.g. 'Kael: Mild Stress')",
        default=""
    )

    brief = SceneBriefInput(
        characters_in_scene=characters_in_scene,
        act_position=act_position,
        previous_scene_summary=previous_summary,
        scene_plot_function=plot_function,
        new_state_goal=new_state_goal,
        character_knowledge=character_knowledge,
        character_emotional_states=emotional_states,
    )

    console.print()
    with console.status("[cyan]Drafting scene (Sonnet)...[/cyan]"):
        final_state = writing_graph.invoke(
            {"scene_brief": brief},
            config=config,
        )

    scene_draft = final_state.get("scene_draft", "")
    rolling_update = final_state.get("rolling_state_update", "")
    completed_scene_number = final_state.get("scene_number", scene_number)

    # Display scene
    console.print()
    console.print(Rule(f"[bold]Scene {completed_scene_number} — {act_position}[/bold]"))
    console.print()
    console.print(scene_draft)

    # Display rolling state
    console.print()
    console.print(Panel(
        rolling_update,
        title="[bold cyan]Rolling State Update[/bold cyan]",
        border_style="cyan"
    ))

    # Offer to export
    if Confirm.ask("\nAppend scene to scenes_output.md?", default=True):
        updated_store = load_store_from_state(final_state)
        export_scenes_to_markdown(updated_store)


@app.command()
def status(db_path: str = typer.Option(DEFAULT_DB_PATH, help="Path to SQLite DB file")):
    """Print a summary of the current engine store."""
    _, writing_graph = get_graphs(db_path)
    config = get_config()

    checkpoint = writing_graph.checkpointer.get(config)
    if not checkpoint:
        console.print("[yellow]No engine store found. Run setup first.[/yellow]")
        raise typer.Exit()

    store = load_store_from_state(checkpoint.get("channel_values", {}))

    print_header("ENGINE STORE STATUS")
    console.print(f"[bold]Premise:[/bold] {store.premise}")
    console.print(f"[bold]Genre/Tone:[/bold] {store.genre_tone}")
    console.print(f"[bold]Setup complete:[/bold] {store.setup_complete}")
    console.print(f"[bold]Characters:[/bold] {', '.join(store.character_machines.keys()) or 'None'}")
    console.print(f"[bold]Relationships:[/bold] {', '.join(store.relationships.keys()) or 'None'}")
    console.print(f"[bold]Scenes written:[/bold] {len(store.scene_history)}")
    console.print()
    console.print("[bold]Current Rolling State:[/bold]")
    console.print(store.rolling_state)


@app.command()
def export(db_path: str = typer.Option(DEFAULT_DB_PATH, help="Path to SQLite DB file")):
    """Export all scenes to Markdown and engine store to JSON."""
    _, writing_graph = get_graphs(db_path)
    config = get_config()

    checkpoint = writing_graph.checkpointer.get(config)
    if not checkpoint:
        console.print("[yellow]No engine store found.[/yellow]")
        raise typer.Exit()

    store = load_store_from_state(checkpoint.get("channel_values", {}))
    export_scenes_to_markdown(store)
    export_store_to_file(store)
    console.print("[green]Export complete.[/green]")


@app.command()
def reset(db_path: str = typer.Option(DEFAULT_DB_PATH, help="Path to SQLite DB file")):
    """Delete the engine store and start fresh. Irreversible."""
    if Confirm.ask(
        f"[red]This will delete {db_path} and all stored data. Are you sure?[/red]",
        default=False
    ):
        reset_store(db_path)
    else:
        console.print("Reset cancelled.")


if __name__ == "__main__":
    app()
