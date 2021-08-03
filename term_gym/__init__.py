from gym.envs.registration import register

register(
    id='TermENV-v0',
    entry_point='term_gym.envs:TermENV',
)
