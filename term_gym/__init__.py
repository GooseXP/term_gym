from gym.envs.registration import register

register(
    id='TermEnv-v0',
    entry_point='term_gym.envs:TermEnv',
)
