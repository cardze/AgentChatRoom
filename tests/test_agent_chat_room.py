import unittest

from agent_chat_room import AgentChatRoom


class TestAgentChatRoom(unittest.TestCase):
    def test_public_and_private_chat_are_stored(self):
        chat = AgentChatRoom(["alpha", "beta", "gamma"])

        chat.post_public("hello everyone")
        chat.send_private("beta", "hi beta")

        self.assertEqual(len(chat.public_messages()), 1)
        self.assertEqual(chat.public_messages()[0].content, "hello everyone")

        self.assertEqual(len(chat.private_messages("beta")), 1)
        self.assertEqual(chat.private_messages("beta")[0].sender, "alpha")

    def test_switching_agent_reads_same_private_room(self):
        chat = AgentChatRoom(["alpha", "beta"])
        chat.send_private("beta", "alpha to beta")

        chat.switch_agent("beta")
        chat.send_private("alpha", "beta to alpha")

        messages = chat.private_messages("alpha")
        self.assertEqual([msg.content for msg in messages], ["alpha to beta", "beta to alpha"])

    def test_invalid_actions_raise_errors(self):
        chat = AgentChatRoom(["alpha", "beta"])

        with self.assertRaises(ValueError):
            chat.post_public("   ")

        with self.assertRaises(ValueError):
            chat.send_private("alpha", "self chat")

        with self.assertRaises(ValueError):
            chat.switch_agent("unknown")


if __name__ == "__main__":
    unittest.main()
