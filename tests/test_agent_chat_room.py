import unittest

from agent_chat_room import AgentChatRoom


class TestAgentChatRoom(unittest.TestCase):
    def test_public_and_private_messages_storage_and_content(self):
        chat = AgentChatRoom(["alpha", "beta", "gamma"])

        chat.post_public("hello everyone")
        chat.send_private("beta", "hi beta")

        self.assertEqual(len(chat.public_messages()), 1)
        self.assertEqual(chat.public_messages()[0].content, "hello everyone")

        self.assertEqual(len(chat.private_messages("beta")), 1)
        self.assertEqual(chat.private_messages("beta")[0].sender, "alpha")

    def test_private_room_persists_across_agent_switches(self):
        chat = AgentChatRoom(["alpha", "beta"])
        chat.send_private("beta", "alpha to beta")

        chat.switch_agent("beta")
        chat.send_private("alpha", "beta to alpha")

        messages = chat.private_messages("alpha")
        self.assertEqual([msg.content for msg in messages], ["alpha to beta", "beta to alpha"])
        self.assertEqual([msg.sender for msg in messages], ["alpha", "beta"])

    def test_invalid_actions_raise_errors(self):
        chat = AgentChatRoom(["alpha", "beta"])

        with self.assertRaises(ValueError):
            chat.post_public("   ")

        with self.assertRaises(ValueError):
            chat.send_private("alpha", "self chat")

        with self.assertRaises(ValueError):
            chat.switch_agent("unknown")

    def test_invalid_initialization_raises_errors(self):
        with self.assertRaises(ValueError):
            AgentChatRoom(["alpha"])

        with self.assertRaises(ValueError):
            AgentChatRoom(["alpha", "alpha", " "])


if __name__ == "__main__":
    unittest.main()
