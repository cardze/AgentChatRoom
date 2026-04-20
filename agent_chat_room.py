from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Message:
    sender: str
    content: str
    timestamp: datetime


class AgentChatRoom:
    def __init__(self, agents: List[str]) -> None:
        cleaned = [name.strip() for name in agents if name.strip()]
        if len(cleaned) < 2:
            raise ValueError("At least two agents are required")

        self._agents = tuple(dict.fromkeys(cleaned))
        if len(self._agents) < 2:
            raise ValueError("At least two unique agents are required")

        self._current_agent = self._agents[0]
        self._public_bbs: List[Message] = []
        self._private_rooms: Dict[Tuple[str, str], List[Message]] = {}

    @property
    def agents(self) -> Tuple[str, ...]:
        return self._agents

    @property
    def current_agent(self) -> str:
        return self._current_agent

    def switch_agent(self, name: str) -> None:
        if name not in self._agents:
            raise ValueError(f"Unknown agent: {name}")
        self._current_agent = name

    def post_public(self, content: str) -> Message:
        return self._store_message(self._public_bbs, content)

    def send_private(self, recipient: str, content: str) -> Message:
        if recipient == self._current_agent:
            raise ValueError("Cannot create one-to-one chat with yourself")
        if recipient not in self._agents:
            raise ValueError(f"Unknown agent: {recipient}")

        room_key = tuple(sorted((self._current_agent, recipient)))
        room = self._private_rooms.setdefault(room_key, [])
        return self._store_message(room, content)

    def public_messages(self) -> List[Message]:
        return list(self._public_bbs)

    def private_messages(self, peer: str) -> List[Message]:
        if peer == self._current_agent:
            raise ValueError("Cannot open one-to-one chat with yourself")
        if peer not in self._agents:
            raise ValueError(f"Unknown agent: {peer}")

        room_key = tuple(sorted((self._current_agent, peer)))
        return list(self._private_rooms.get(room_key, []))

    def _store_message(self, room: List[Message], content: str) -> Message:
        text = content.strip()
        if not text:
            raise ValueError("Message content cannot be empty")

        message = Message(
            sender=self._current_agent,
            content=text,
            timestamp=datetime.now(timezone.utc),
        )
        room.append(message)
        return message


def _format_messages(messages: List[Message]) -> str:
    if not messages:
        return "(no messages yet)"

    lines = []
    for message in messages:
        stamp = message.timestamp.strftime("%H:%M:%S")
        lines.append(f"[{stamp}] {message.sender}: {message.content}")
    return "\n".join(lines)


def run_cli() -> None:
    print("Agent Chat Room")
    print("Enter agent names separated by commas (example: alpha,beta,gamma):")
    raw = input("> ").strip()
    chat = AgentChatRoom(raw.split(","))

    print("\nType /help to view commands.")

    while True:
        prompt = f"{chat.current_agent}> "
        try:
            command = input(prompt).strip()
        except EOFError:
            print("\nBye")
            return

        if not command:
            continue

        if command == "/help":
            print("Commands:")
            print("  /agents                 List available agents")
            print("  /switch <agent>         Switch active speaker")
            print("  /post <message>         Post message to public BBS")
            print("  /public                 Show public BBS messages")
            print("  /dm <agent> <message>   Send private message")
            print("  /chat <agent>           Show one-to-one room")
            print("  /quit                   Exit")
            continue

        if command == "/quit":
            print("Bye")
            return

        if command == "/agents":
            print(", ".join(chat.agents))
            continue

        if command.startswith("/switch "):
            _, _, name = command.partition(" ")
            try:
                chat.switch_agent(name.strip())
                print(f"Switched to {chat.current_agent}")
            except ValueError as error:
                print(error)
            continue

        if command.startswith("/post "):
            _, _, text = command.partition(" ")
            try:
                chat.post_public(text)
                print("Posted to public BBS")
            except ValueError as error:
                print(error)
            continue

        if command == "/public":
            print("Public BBS:")
            print(_format_messages(chat.public_messages()))
            continue

        if command.startswith("/dm "):
            parts = command.split(maxsplit=2)
            if len(parts) < 3:
                print("Usage: /dm <agent> <message>")
                continue
            _, recipient, text = parts
            try:
                chat.send_private(recipient, text)
                print(f"Sent private message to {recipient}")
            except ValueError as error:
                print(error)
            continue

        if command.startswith("/chat "):
            _, _, peer = command.partition(" ")
            peer = peer.strip()
            try:
                messages = chat.private_messages(peer)
                print(f"Private chat with {peer}:")
                print(_format_messages(messages))
            except ValueError as error:
                print(error)
            continue

        print("Unknown command. Use /help")


if __name__ == "__main__":
    try:
        run_cli()
    except ValueError as error:
        print(f"Setup error: {error}")
