import os
from typing import Dict, List

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, OptionList, Static
from textual.widgets.option_list import Option

from ignore.utils import get_file, get_template_list, validate_gitignore_response


class GitignoreTUI(App):
    """A simplified TUI for gitignore-create"""

    CSS = """
    Screen {
        background: $surface;
    }

    #search-container {
        height: 3;
        padding: 0 1;
    }

    #main-container {
        height: 100%;
    }

    #left-panel {
        width: 40%;
        padding: 1;
    }

    #right-panel {
        width: 60%;
        padding: 1;
    }

    #template-list {
        height: 100%;
        border: solid $primary;
    }

    #preview-box {
        height: 100%;
        border: solid $primary;
    }

    #output-container {
        height: 3;
        padding: 0 1;
    }

    #button-container {
        height: 3;
        padding: 0 1;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("space", "toggle", "Toggle"),
    ]

    def __init__(self):
        super().__init__()
        self.all_templates: List[str] = []
        self.filtered_templates: List[str] = []
        self.selected_templates: List[str] = []
        self.content_cache: Dict[str, str] = {}  # Cache for fetched template content

    def compose(self) -> ComposeResult:
        yield Header()

        # Search box
        with Container(id="search-container"):
            yield Input(placeholder="Search templates...", id="search-input")

        # Main container with left (list) and right (preview) panels
        with Horizontal(id="main-container"):
            with Vertical(id="left-panel"):
                yield Label("Templates (Space to select, Enter to preview):")
                yield OptionList(id="template-list")

            with Vertical(id="right-panel"):
                yield Label("Preview:")
                yield Static("Select a template and press Enter to preview", id="preview-box")

        # Output path input
        with Container(id="output-container"):
            yield Input(value="./", placeholder="Output path", id="output-input")

        # Buttons
        with Horizontal(id="button-container"):
            yield Button("Generate", variant="primary", id="generate-btn")
            yield Button("Cancel", id="cancel-btn")

        yield Footer()

    async def on_mount(self) -> None:
        """Load templates when app starts"""
        self.title = "gitignore-create"

        # Fetch templates
        try:
            # get_template_list() now returns sorted results
            self.all_templates = get_template_list()
            self.filtered_templates = self.all_templates.copy()
            await self.populate_list()
        except RuntimeError as e:
            preview = self.query_one("#preview-box", Static)
            preview.update(f"Error loading templates: {e}")
        except Exception as e:
            preview = self.query_one("#preview-box", Static)
            preview.update(f"Unexpected error loading templates: {e}")

    async def populate_list(self):
        """Populate the template list"""
        option_list = self.query_one("#template-list", OptionList)
        option_list.clear_options()

        for template in self.filtered_templates:
            prefix = "[x] " if template in self.selected_templates else "[ ] "
            option_list.add_option(Option(f"{prefix}{template}", id=template))

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes"""
        if event.input.id == "search-input":
            query = event.value.lower()
            if query:
                self.filtered_templates = [
                    t for t in self.all_templates if query in t.lower()
                ]
            else:
                self.filtered_templates = self.all_templates.copy()
            await self.populate_list()

    async def action_toggle(self) -> None:
        """Toggle selection of highlighted template"""
        option_list = self.query_one("#template-list", OptionList)
        highlighted = option_list.highlighted

        if highlighted is not None:
            template = self.filtered_templates[highlighted]

            if template in self.selected_templates:
                self.selected_templates.remove(template)
            else:
                self.selected_templates.append(template)

            await self.populate_list()
            option_list.highlighted = highlighted

    async def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle template selection - show preview"""
        template = event.option.id
        if template:
            await self.show_preview([template])

    async def show_preview(self, templates: List[str]):
        """Fetch and display preview of templates"""
        preview = self.query_one("#preview-box", Static)

        # Create cache key from sorted template list
        cache_key = ','.join(sorted(templates))

        try:
            # Check cache first
            if cache_key in self.content_cache:
                content = self.content_cache[cache_key]
            else:
                preview.update("Loading preview...")
                content = get_file(templates)
                # Cache the result
                self.content_cache[cache_key] = content

            if not validate_gitignore_response(content):
                preview.update("Error: Template not found")
            else:
                preview.update(content)
        except RuntimeError as e:
            preview.update(f"Error: {e}")
        except Exception as e:
            preview.update(f"Unexpected error: {e}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "cancel-btn":
            self.exit()
        elif event.button.id == "generate-btn":
            await self.generate_gitignore()

    async def generate_gitignore(self):
        """Generate .gitignore file"""
        if not self.selected_templates:
            preview = self.query_one("#preview-box", Static)
            preview.update("Error: Please select at least one template (use Space)")
            return

        output_input = self.query_one("#output-input", Input)
        output_path = output_input.value or "./"
        preview = self.query_one("#preview-box", Static)

        # Create cache key from sorted template list
        cache_key = ','.join(sorted(self.selected_templates))

        try:
            # Check cache first (likely already cached from preview)
            if cache_key in self.content_cache:
                content = self.content_cache[cache_key]
            else:
                content = get_file(self.selected_templates)
                self.content_cache[cache_key] = content

            if not validate_gitignore_response(content):
                preview.update("Error: Failed to fetch templates")
                return

            gitignore_path = os.path.join(output_path, '.gitignore')
            with open(gitignore_path, "w") as f:
                f.write(content)

            preview.update(f"Success! File written to {gitignore_path}\n\nPress q to quit")

        except RuntimeError as e:
            preview.update(f"Error: {e}")
        except OSError as e:
            preview.update(f"Error writing file: {e}")
        except Exception as e:
            preview.update(f"Unexpected error: {e}")
