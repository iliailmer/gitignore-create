import os
from typing import List

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, ListView, ListItem, Static
from textual.binding import Binding

from ignore.utils import get_file, get_template_list


class TemplateListItem(ListItem):
    """A list item that can be selected/deselected"""

    def __init__(self, template_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = template_name
        self.is_selected = False

    def compose(self) -> ComposeResult:
        yield Label(f"[ ] {self.template_name}")

    def toggle_selection(self):
        """Toggle selection state"""
        self.is_selected = not self.is_selected
        label = self.query_one(Label)
        if self.is_selected:
            label.update(f"[x] {self.template_name}")
        else:
            label.update(f"[ ] {self.template_name}")


class GitignoreTUI(App):
    """A Textual TUI for gitignore-create"""

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
        border: solid $primary;
        padding: 1;
    }

    #right-panel {
        width: 60%;
        border: solid $primary;
        padding: 1;
        overflow-y: scroll;
    }

    #template-list {
        height: 100%;
        border: solid $accent;
    }

    #preview-box {
        height: 100%;
        border: solid $accent;
        overflow-y: scroll;
    }

    #output-container {
        height: 5;
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
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.all_templates: List[str] = []
        self.filtered_templates: List[str] = []
        self.selected_templates: List[str] = []

    def compose(self) -> ComposeResult:
        yield Header()

        # Search box
        with Container(id="search-container"):
            yield Label("Search templates:")
            yield Input(placeholder="Type to search...", id="search-input")

        # Main container with left (list) and right (preview) panels
        with Horizontal(id="main-container"):
            with Vertical(id="left-panel"):
                yield Label("Available Templates (click to select):")
                yield ListView(id="template-list")

            with Vertical(id="right-panel"):
                yield Label("Preview:")
                yield Static("Select templates to preview", id="preview-box")

        # Output path input
        with Container(id="output-container"):
            yield Label("Output path:")
            yield Input(value="./", placeholder="./", id="output-input")

        # Buttons
        with Horizontal(id="button-container"):
            yield Button("Generate", variant="primary", id="generate-btn")
            yield Button("Cancel", variant="error", id="cancel-btn")

        yield Footer()

    async def on_mount(self) -> None:
        """Load templates when app starts"""
        self.title = "gitignore-create TUI"

        # Fetch templates
        try:
            self.all_templates = get_template_list()
            self.all_templates.sort()
            self.filtered_templates = self.all_templates.copy()
            await self.populate_list()
        except Exception as e:
            preview = self.query_one("#preview-box", Static)
            preview.update(f"Error loading templates: {e}")

    async def populate_list(self):
        """Populate the template list"""
        list_view = self.query_one("#template-list", ListView)
        await list_view.clear()

        for template in self.filtered_templates:
            item = TemplateListItem(template)
            # Restore selection state if it was previously selected
            if template in self.selected_templates:
                item.toggle_selection()
            await list_view.append(item)

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

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle template selection"""
        if isinstance(event.item, TemplateListItem):
            event.item.toggle_selection()

            # Update selected templates list
            if event.item.is_selected:
                if event.item.template_name not in self.selected_templates:
                    self.selected_templates.append(event.item.template_name)
            else:
                if event.item.template_name in self.selected_templates:
                    self.selected_templates.remove(event.item.template_name)

            # Update preview
            await self.update_preview()

    async def update_preview(self):
        """Fetch and display preview of selected templates"""
        preview = self.query_one("#preview-box", Static)

        if not self.selected_templates:
            preview.update("Select templates to preview")
            return

        try:
            preview.update("Loading preview...")
            resp = get_file(self.selected_templates)
            content = resp.content.decode("utf-8")

            if "error" in content.lower():
                preview.update(f"Error: Template not found")
            else:
                preview.update(content)
        except Exception as e:
            preview.update(f"Error loading preview: {e}")

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
            preview.update("Error: Please select at least one template")
            return

        output_input = self.query_one("#output-input", Input)
        output_path = output_input.value or "./"

        try:
            resp = get_file(self.selected_templates)
            content = resp.content.decode("utf-8")

            if "error" in content.lower():
                preview = self.query_one("#preview-box", Static)
                preview.update("Error: Failed to fetch templates")
                return

            gitignore_path = os.path.join(output_path, '.gitignore')
            with open(gitignore_path, "w") as f:
                f.write(content)

            preview = self.query_one("#preview-box", Static)
            preview.update(f"Success! File written to {gitignore_path}")

        except Exception as e:
            preview = self.query_one("#preview-box", Static)
            preview.update(f"Error writing file: {e}")
