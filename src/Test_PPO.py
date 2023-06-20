import unittest
import torch
import os
from ppo_torch import Buffer, PPOAgent
class TestReinforcementLearning(unittest.TestCase):
    def setUp(self):
        self.buffer = Buffer()
        self.agent = PPOAgent(state_dim=3, price_action_dim=2, volume_action_dim=2, lr_actor=0.01, lr_critic=0.01, 
                              gamma=0.99, n_epochs=10, eps_clip=0.2, device=torch.device("cpu"))
        self.dummy_state = torch.tensor([1.0, 2.0, 3.0])
        self.dummy_reward = 1.0
        self.dummy_done = False
        self.checkpoint_path = "agent_checkpoint.pth"

    def test_buffer(self):
        self.buffer.store_memory(self.dummy_state, 0, 1, 0.5, 0.5, 0.5, self.dummy_reward, self.dummy_done)
        self.assertEqual(len(self.buffer.states), 1)
        self.buffer.clear()
        self.assertEqual(len(self.buffer.states), 0)

    def test_agent_action(self):
        price_action, volume_action, price_action_logprob, volume_action_logprob, state_value = self.agent.select_action(self.dummy_state)
        self.assertIsInstance(price_action, torch.Tensor)
        self.assertIsInstance(volume_action, torch.Tensor)
        self.assertTrue(0 <= price_action.item() < self.agent.policy.price_output[0].out_features)
        self.assertTrue(0 <= volume_action.item() < self.agent.policy.volume_output[0].out_features)

    def test_agent_memory(self):
        self.agent.send_memory_to_buffer(self.dummy_state, torch.tensor([0]), torch.tensor([1]), 0.5, 0.5, 0.5, self.dummy_reward, self.dummy_done)
        self.assertEqual(len(self.agent.buffer.states), 1)
        self.agent.buffer.clear()
        self.assertEqual(len(self.agent.buffer.states), 0)

    def test_agent_update(self):
         state_dim = 3
         price_action_dim = 2
         volume_action_dim = 2
         num_samples = 100  # Number of states to generate

          # Generate dummy states
         dummy_states = torch.randn(num_samples, state_dim)

         # Store dummy states in the buffer
         for state in dummy_states:
             self.agent.send_memory_to_buffer(state, torch.tensor([0]), torch.tensor([1]), 
                                         torch.tensor([0.5]), torch.tensor([0.5]), 
                                         torch.tensor([0.5]), torch.tensor([self.dummy_reward]), 
                                         torch.tensor([self.dummy_done]))

        # Test the agent's update method
         old_policy_dict = self.agent.policy.state_dict()
         self.agent.update()
         self.assertEqual(len(self.agent.buffer.states), 0)  # Check that buffer was cleared after update

         new_policy_dict = self.agent.policy.state_dict()
         for (old_param, new_param) in zip(old_policy_dict.values(), new_policy_dict.values()):
            self.assertFalse(torch.equal(old_param, new_param))  # Check that weights have changed after update


    def test_agent_save_and_load(self):
        self.agent.save(self.checkpoint_path)
        self.agent.load(self.checkpoint_path)
        for old_param, new_param in zip(self.agent.policy_old.parameters(), self.agent.policy.parameters()):
            self.assertTrue(torch.equal(old_param, new_param))

    def tearDown(self):
        # Cleanup after each test
        if os.path.exists(self.checkpoint_path):
            os.remove(self.checkpoint_path)


if __name__ == '__main__':
    unittest.main()