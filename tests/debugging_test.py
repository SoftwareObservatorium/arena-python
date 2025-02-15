# https://stackoverflow.com/questions/14243956/dynamically-creating-classes-with-eval-in-python
def test_adapter_class():
    init = """def cls_init(self, param):\n\tself.type = 3"""
    cls_init = exec(init)

    my_clazz = type("adapter.MyClass", (object,), {'__init__': cls_init})

    # add more functions/methods
    my_clazz.my_method = len

    print(my_clazz)