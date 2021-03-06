import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os, sys

def init_para(D, K, h):
    # initialize parameters randomly
    W = np.random.normal(0, 0.01, (D, h))
    b = np.zeros((1, h), dtype = float)
    W2 = np.random.normal(0, 0.01, (h, K))
    b2 = np.zeros((1, K), dtype = float)
    return W, b, W2, b2

def softmax(scores):
    exp_scores = np.exp(scores)
    return exp_scores / np.sum(exp_scores, axis = 1).reshape(-1, 1)

def nnet(X, y, step_size = 0.4, lam = 0.0001, h = 10, num_iters = 1000):
    # get dim of input
    N, D = X.shape
    K = y.shape[1]

    W, b, W2, b2 = init_para(D, K, h)

    # gradient descent loop to update weight and bias
    for i in range(num_iters):
        # hidden layer, ReLU activation
        hidden_layer = np.maximum(0, np.dot(X, W) + np.repeat(b, N, axis = 0))

        # class score
        scores = np.dot(hidden_layer, W2) + np.repeat(b2, N, axis = 0)

        # compute and normalize class probabilities
        probs = softmax(scores)

        # compute the loss with regularization
        data_loss = np.sum(-np.log(probs) * y) / N
        reg_loss = 0.5 * lam * np.sum(W * W) + 0.5 * lam * np.sum(W2 * W2)
        loss = data_loss + reg_loss

        # check progress
        if i%1000 == 0 or i == num_iters:
            print("iteration {}: loss {}".format(i, loss))

        # compute the gradient on scores
        dscores = (probs - y) / N

        # backpropate the gradient to the parameters
        dW2 = np.dot(hidden_layer.T, dscores)
        db2 = np.sum(dscores, axis = 0)
        # next backprop into hidden layer
        dhidden = np.dot(dscores, W2.T)
        # backprop the ReLU non-linearity
        dhidden[hidden_layer <= 0] = 0
        # finally into W,b
        dW = np.dot(X.T, dhidden)
        db = np.sum(dhidden, axis = 0)

        # add regularization gradient contribution
        dW2 = dW2 + lam * W2
        dW = dW + lam * W

        # update parameter
        W = W - step_size * dW
        b = b - step_size * db
        W2 = W2 - step_size * dW2
        b2 = b2 - step_size * db2
    return W, b, W2, b2

def predict(X, para):
    W, b, W2, b2 = para
    N = X.shape[0]
    hidden_layer = np.maximum(0, np.dot(X, W) + np.repeat(b, N, axis = 0))
    scores = np.dot(hidden_layer, W2) + np.repeat(b2, N, axis = 0)
    return np.argmax(scores, axis = 1)

if __name__ == '__main__':
    images_dir = os.path.join(sys.path[0], 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    N = 80 # number of points per class
    D = 2 # dimensionality, we use 2D data for easy visulization
    K = 4 # number of classes, binary for logistic regression
    X = np.zeros((N * K, D), dtype = float) # data matrix (each row = single example, can view as xy coordinates)
    y_ = np.zeros(N * K, dtype = int) # class labels for plotting
    y = np.zeros((N * K, K), dtype = int) # class labels for training


    for i in range(K):
        r = np.linspace(0.05, 1, N).reshape(-1, 1) # radius
        t = np.linspace(i*4.7, (i+1)*4.7, N).reshape(-1, 1) + np.random.normal(0, 0.3, (N, 1)) # theta

        X[i * N:(i + 1) * N] = np.append(r * np.sin(t), r * np.cos(t), axis = 1)
        y_[i * N:(i + 1) * N] = i
        y[i * N:(i + 1) * N, i] = 1

    num_iters = 10000
    para = nnet(X, y, step_size = 0.3, lam = 0.0005, h = 50, num_iters = num_iters)
    predicted = predict(X, para)
    print('The accuracy is {:.2f} %'.format(sum(predicted == y_)/len(y_)*100))

    grid_size = 200
    u = np.linspace(min(X[:, 0]),max(X[:, 0]), grid_size)
    v = np.linspace(min(X[:, 1]),max(X[:, 1]), grid_size)

    gridx, gridy = np.meshgrid(u, v)
    grid = np.array([gridx.reshape(-1, ), gridy.reshape(-1, )]).T
    z = predict(grid, para).reshape(grid_size, grid_size)

    plt.contourf(u,v,z, alpha = 0.2, levels = K - 1, antialiased = True)
    sns.scatterplot(x = X[:, 0], y = X[:, 1], hue = y_, palette = sns.color_palette('deep', K), edgecolor = "none")
    plt.title('Decision Boundary')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.savefig(os.path.join(images_dir, 'decision_boundary_nnet.png'))
    plt.clf()
