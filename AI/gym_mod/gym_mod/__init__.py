from gymnasium.envs.registration import register

register(
    id='BT_TCG_v0',
    entry_point='gym_mod.envs:BattleTechEnv',
    max_episode_steps=10000,
)
