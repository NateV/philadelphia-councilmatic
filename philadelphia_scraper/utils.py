


class PassthroughDict:
    """
    Like a Dict, but if the key is not in the dict, it returns the key instead.
    """

    def __init__(self, the_dict: dict): 
        self.the_dict = the_dict

    def __call__(self, key):
        """
        Get the value stored in the dict at `key`, or return the key.
        """
        return self.the_dict.get(key) or key


name_adjuster = PassthroughDict({
        "Quetcy Lozada": "Quetcy M. Lozada",
        "Kathrine Gilmore Richardson": "Katherine Gilmore Richardson"
    })

