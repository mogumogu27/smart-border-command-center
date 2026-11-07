def score(input):
    if input[2] <= 21.0:
        if input[2] <= 15.5:
            var0 = [0.0, 1.0, 0.0]
        else:
            if input[3] <= 0.5:
                var0 = [0.0, 1.0, 0.0]
            else:
                var0 = [0.0, 0.0, 1.0]
    else:
        if input[2] <= 35.5:
            var0 = [0.0, 0.0, 1.0]
        else:
            var0 = [1.0, 0.0, 0.0]
    return var0
