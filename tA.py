class A():
    def __init__(self, *args, **kwargs):
        pass

    def out(self,*args):
        print("A out %s" % args[0])