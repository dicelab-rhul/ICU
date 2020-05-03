if __name__ == "__main__":

    import random

    from  icu.eyetracking.filter import IVTFilter, NWMAFilter

    ivt = IVTFilter(4)

    for i in range(4):
        v = ivt(i, random.randint(0,10), random.randint(0,10))
        print(v)


    nwma = NWMAFilter(1)

    for i in range(4):
        v = nwma(i, random.randint(0,10), random.randint(0,10))
        print(v)


    