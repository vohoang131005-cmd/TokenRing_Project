
# utils/ui.py
import threading
import time

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import WindowAlign
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import Frame, TextArea
from prompt_toolkit.formatted_text import FormattedText

import utils.logger as logger


class TerminalUI:
    def __init__(self, node_id, on_submit_callback):

        self.node_id = node_id
        self.on_submit_callback = on_submit_callback

        self.status_text = "Dang khoi dong..."
        self.is_holding = False
        self.log_lines = []

        # Thong tin ky thuat
        self.lamport_time = 0
        self.token_uuid = "init"
        self.vector_clock = [0] * 6

        self.input_field = TextArea(
            height=1,
            prompt=f"Node {self.node_id} > ",
            accept_handler=self._accept_input,
            multiline=False
        )

        self.status_window = Window(
            content=FormattedTextControl(
                self._get_status_text
            ),
            height=1,
            align=WindowAlign.CENTER
        )

        # Khung LOG
        log_window = Frame(
            Window(
                content=FormattedTextControl(
                    self._get_log_text
                ),
                wrap_lines=True
            ),
            title=f"LOG NODE {self.node_id}"
        )

        # Khung TECH INFO
        tech_window = Frame(
            Window(
                content=FormattedTextControl(
                    self._get_tech_text
                ),
                wrap_lines=True
            ),
            title="TECH INFO",
            width=30
        )

        middle_container = VSplit([
            log_window,
            tech_window
        ])

        root_container = HSplit([
            Frame(
                self.status_window,
                title="TRANG THAI",
                height=3
            ),
            middle_container,
            Frame(
                self.input_field,
                title="NHAP DU LIEU"
            )
        ])

        self.layout = Layout(root_container)

        self.app = Application(
            layout=self.layout,
            full_screen=True,
            key_bindings=self._get_key_bindings()
        )

        self.layout.focus(self.input_field)

    def _get_log_text(self):

        display_lines = self.log_lines[-15:]

        if not display_lines:
            return FormattedText([
                ("class:log", "Chua co log...")
            ])

        formatted = []

        for line in display_lines:
            formatted.append(
                ("class:log", line + "\n")
            )

        return FormattedText(formatted)

    def _get_status_text(self):

        if self.is_holding:
            return FormattedText([
                (
                    "class:status-holding",
                    f" DANG GIU TOKEN - {self.status_text} "
                )
            ])

        return FormattedText([
            (
                "class:status-waiting",
                f" {self.status_text} "
            )
        ])

    def _get_tech_text(self):

        vector_text = ", ".join(
            str(x) for x in self.vector_clock
        )

        lines = [
            f"Lamport:\n{self.lamport_time}",
            f"\nUUID Token:\n{str(self.token_uuid)[:8]}...",
            f"\nNode ID:\n{self.node_id}",
            f"\nVector Clock:\n[{vector_text}]"
        ]

        return FormattedText([
            ("class:tech", "\n".join(lines))
        ])

    def _accept_input(self, buffer):

        text = buffer.text.strip()

        if text:
            self.on_submit_callback(text)
            buffer.text = ""

        return True

    def _get_key_bindings(self):

        kb = KeyBindings()

        @kb.add("c-c")
        def exit_(event):
            event.app.exit()

        return kb

    def update_status(self, status, is_holding):

        self.status_text = status
        self.is_holding = is_holding

        self.app.invalidate()

    def update_tech_info(
        self,
        lamport_time,
        token_uuid,
        vector_clock
    ):

        self.lamport_time = lamport_time
        self.token_uuid = token_uuid
        self.vector_clock = list(vector_clock)

        self.app.invalidate()

    def update_logs(self):

        self.log_lines = logger.LOGS.get(
            self.node_id,
            []
        )

        self.app.invalidate()

    def run(self):

        from prompt_toolkit.styles import Style

        style = Style.from_dict({
            "status-holding": "bg:#00aa00 #ffffff bold",
            "status-waiting": "bg:#888888 #ffffff",
            "log": "#ffffff",
            "tech": "#00ffff"
        })

        self.app.style = style

        def watch_logs():

            last_len = 0

            while True:

                logs = logger.LOGS.get(
                    self.node_id,
                    []
                )

                if len(logs) != last_len:
                    self.update_logs()
                    last_len = len(logs)

                time.sleep(0.1)

        threading.Thread(
            target=watch_logs,
            daemon=True
        ).start()

        self.app.run()
