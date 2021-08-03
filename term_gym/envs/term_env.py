import numpy as np
from pathlib import Path
import gym
from gym import spaces
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired


class TermENV(gym.Env):

    def __init__(self):
        self.range = .48  # +/- the value number can be between
        self.bounds = 10000  # Action space bounds

        self.observation_space = spaces.Box(
            low=np.array([-self.bounds]).astype(np.float32),
            high=np.array([self.bounds]).astype(np.float32),
        )
        self.nb_actions = 96
        self.observation = np.atleast_3d((np.frombuffer((str(Path.cwd()) + '> ').encode(), dtype=np.uint8) - 31) / 100)
        self.action_space = spaces.Discrete(self.nb_actions)
        self.length_penalty = .25
        self.learning_reward = 1
        self.variety_reward = 5
        self.max_cmd = 100
        self.blank_penalty = self.max_cmd * self.length_penalty
        self.reset()

    def step(self, action):
        done = False
        enc_ascii = np.argmax(action) + 32
        if len(self.cmd) < self.max_cmd:
            if enc_ascii != 127:
                self.cmd += chr(enc_ascii)
                done = False
            else:
                done = True
        if done:
            if not self.cmd:
                self.reward -= self.blank_penalty
            proc = Popen(self.cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            try:
                stdout = proc.communicate(timeout=5)[0].decode()
                exitcode = proc.returncode
            except TimeoutExpired:
                proc.kill()
                stdout = proc.communicate()[0].decode()
                exitcode = proc.returncode
            self.term_out = ''.join(char for char in stdout if char.isprintable())
            input_data = self.term_out + ' ' + str(Path.cwd()) + '> '
            filename = Path('mem.txt')
            filename.touch(exist_ok=True)
            if exitcode == 0:
                with open('mem.txt', 'r+') as mem:
                    for line in stdout.splitlines():
                        if line + '\n' not in mem:
                            mem.write(line + '\n')
                            self.reward += self.learning_reward
            print('\n')
            print(stdout)
            print(str(Path.cwd()) + '> ', end='', flush=True)
        else:
            input_data = self.term_out + ' ' + str(Path.cwd()) + '> ' + self.cmd
            print(input_data[-1], end='', flush=True)
            if self.prev_cmd:
                if self.cmd[-1] not in self.prev_cmd:
                    self.reward += self.variety_reward
            self.prev_cmd = self.cmd
            self.reward -= self.length_penalty
        self.observation = np.atleast_3d((np.frombuffer(input_data.encode(), dtype=np.uint8) - 31) / 100)
        return self.observation, self.reward, done

    def reset(self):
        self.observation = np.atleast_3d((np.frombuffer((str(Path.cwd()) + '> ').encode(), dtype=np.uint8) - 31) / 100)
        self.reward = 0
        self.term_out = ''
        self.prev_cmd = ''
        self.cmd = ''
        return self.observation
