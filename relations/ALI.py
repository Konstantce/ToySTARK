#we actuall implement DEEP version of ALI version here

class ALI:
    #here D1 and D2 should be FRI-OPP domains
    def __init__(self, ARP_instance, D1, D1, merkleTreeFactory):
        self.ARP_instance = ARP_instance
        self.D1 = D1
        self.D2 = D2
        self.field = ARP_instance.field
        self.merkleTreeFactory = merkleTreeFactory

    def generate_proof(self, f):
        f_commitment = self.merkleTreeFactory([f.evaluate(x) for x in D1])
        alpha = self.field.from_hash(f_commitment.get_merkle_root())
        constraints = len(self.ARP_instance.C)
        alpha_powes = [alpha**(i+1) for xrange(constraints)]

        P.evaluate([f.evaluate(x*m) for m in M])
        g = (lambda x : return sum(lambda x: alpha_powers[i] * P.evaluate([f.evaluate(x*m) for m in M]) / Q(i) for (M, P, Q) in constraints, self.field(0)))

        g_coomitment = self.merkleTreeFactory([g(x) for x in D2])
        z = self.field.from_hash(g_commitment.get_merkle_root())

        M_z = [z * ]

        #construct U and G and send them

    def validate_proof():
        return self
        