import hashlib
import binascii


class Merkle(object):
    def __init__(self, hash_type="sha256"):
        hash_type = hash_type.lower()
        self.hash_function = getattr(hashlib, hash_type)
        self.reset_tree()


    def reset_tree(self):
        self.leaves = list()
        self.levels = None
        self.is_ready = False


    def add_leaf(self, values, do_hash=False):
        # check if single leaf
        if not isinstance(values, tuple) and not isinstance(values, list):
            values = [values]
        
        for v in values:
            if do_hash:
                v = v.encode('utf-8')
                v = self.hash_function(v).hexdigest()
            
            v = bytearray.fromhex(v)
            self.leaves.append(v)


    def _calculate_next_level(self):
        solo_leave = None

        # number of leaves on the level
        N = len(self.levels[0])
        
        # if odd number of leaves on the level
        if N % 2 == 1:
            solo_leave = self.levels[0][-1]
            N -= 1

        new_level = []
        
        for l, r in zip(self.levels[0][0:N:2], self.levels[0][1:N:2]):
            new_level.append(self.hash_function(l+r).digest())
        
        if solo_leave is not None:
            new_level.append(solo_leave)
        
        # prepend new level
        self.levels = [new_level, ] + self.levels


    def make_tree(self):
        if self.leaves:
            self.levels = [self.leaves]
            
            while len(self.levels[0]) > 1:
                self._calculate_next_level()


    def get_merkle_root(self):
        if self.levels is not None:
            return self.levels[0][0].hex()
        
        return None


if __name__ == '__main__':
    m = Merkle()
    m.add_leaf('123', True)
    m.add_leaf('234', True)
    m.add_leaf('345')
    m.make_tree()
    r = m.get_merkle_root()
    print(f'r: {r!r}')