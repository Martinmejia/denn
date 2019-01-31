import numpy as np
import torch
from torch.autograd import grad
import tqdm

class Chanflow(torch.nn.Module):
    """ Basic neural network to approximate the solution of the stationary channel flow PDE """

    def __init__(self, in_dim=1, out_dim=1, num_units=10, num_layers=5):
        """ initializes architecture """
        super().__init__()
        self.activation=torch.nn.Tanh()
        self.layers=torch.nn.ModuleList()
        for i in range(num_layers):
            if i == 0: # input layer
                self.layers.append(torch.nn.Linear(in_dim, num_units))
            elif i == num_layers-1: # output layer
                self.layers.append(torch.nn.Linear(num_units, out_dim))
            else: # hidden layer(s)
                self.layers.append(torch.nn.Linear(num_units, num_units))

    def forward(self, x):
        """ implements a forward pass """
        for i in range(len(self.layers)-1):
            x = self.activation(self.layers[i](x))
        return self.layers[-1](x) # last layer is just linear (regression)

    def train(self, ymin, ymax, reynolds_stress_fn,
              nu=1., dp_dx=-1., rho=1., batch_size=1000,
              epochs=500, lr=0.001, C=1., momentum=0.9):

        """ implements training
        args:
        ymin - y coordinate of the lower plate
        ymax - y coordinate of the upper plate
        reynolds_stress_fn - a function that accepts as arguments (y, du_dy) and returns a reynolds stress
        """

        optimizer=torch.optim.Adam(self.parameters(), lr=lr)
        boundary=torch.tensor(np.array([ymin, ymax]).reshape(-1,1), dtype=torch.float)
        boundary_condition=torch.zeros_like(boundary)
        losses=[]

        with tqdm.trange(epochs) as t:
            for e in t:
                y_batch = ymin + (ymax-ymin)*torch.rand((batch_size,1), requires_grad=True)

                # compute \bar{u} predictions
                u_bar = self(y_batch)

                # adjust for BV conditions
                # u_bar = BV[0] + (BV[1]-BV[0])*(y_batch - boundary[0])/(boundary[1]-boundary[0]) + (y_batch - boundary[0])*(y_batch - boundary[1])*u_bar

                # compute d(\bar{u})/dy
                du_dy, = grad(u_bar, y_batch,
                              grad_outputs=u_bar.data.new(u_bar.shape).fill_(1),
                              retain_graph=True,
                              create_graph=True)

                # compute d^2(\bar{u})/dy^2
                d2u_dy2, = grad(du_dy, y_batch,
                                grad_outputs=du_dy.data.new(du_dy.shape).fill_(1),
                                retain_graph=True,
                                create_graph=True)

                # compute d<uv>/dy
                re = reynolds_stress_fn(y_batch, du_dy)
                dre_dy, = grad(re, y_batch,
                               grad_outputs=re.data.new(re.shape).fill_(1),
                               retain_graph=True,
                               create_graph=True)

                # compute loss!
                axial_eqn = nu * d2u_dy2 - dre_dy - (1/rho) * dp_dx
                boundary_pred = self(boundary)
                loss = torch.mean(torch.pow(axial_eqn, 2)) + C * torch.mean(torch.pow(boundary_condition - boundary_pred, 2))

                # zero grad, backprop, step
                optimizer.zero_grad()
                loss.backward(retain_graph=False, create_graph=False)
                optimizer.step()

                loss = loss.data.numpy()
                losses.append(loss)
                t.set_postfix(loss=np.round(loss, 2))

        return losses

def calc_renot(u_bar, delta, nu):
    n = u_bar.shape[0]
    U_0 = u_bar[n//2][0]
    renot = U_0 * delta / nu
    return renot

def calc_renum(u_bar, ygrid, delta, nu):
    n = u_bar.shape[0]
    U_bar = (1/delta) * np.trapz(u_bar[:n//2], x=ygrid[:n//2], axis=0)[0] # integrate from wall to center
    renum = 2 * delta * U_bar / nu
    return renum

def calc_retau(delta, dp_dx, rho, nu):
    tau_w = -delta * dp_dx
    u_tau = np.sqrt(tau_w / rho)
    re_tau = u_tau * delta / nu
    return re_tau

def get_hyperparams(dp_dx=-1.0, nu=0.001, rho=1.0, k=0.41, num_units=50,
                    num_layers=5, batch_size=1000, lr=0.001, num_epochs=1000,
                    ymin=0, ymax=2):
    """
    dp_dx - pressure gradient
    nu - kinematic viscosity
    rho - density
    k - karman constant (mixing length model), see: https://en.wikipedia.org/wiki/Von_K%C3%A1rm%C3%A1n_constant
    """
    return dict(dp_dx=dp_dx, nu=nu, rho=rho, k=k, num_units=num_units, num_layers=num_layers,
                batch_size=batch_size, lr=lr, num_epochs=num_epochs, ymin=ymin, ymax=ymax)

def get_yspace(n=1000, ymin=-1, ymax=1):
    ygrid = torch.linspace(ymin, ymax, n).reshape(-1,1)
    return torch.autograd.Variable(ygrid, requires_grad=True)

def get_mixing_len_model(k, delta):
    return lambda y, du_dy: -1*((k*(torch.abs(y)-delta))**2)*torch.abs(du_dy)*du_dy

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    print('Testing channel flow NN...')
    # hyperparams
    hypers = get_hyperparams(ymin=-1, ymax=1, num_epochs=2000, lr=0.001, num_layers=4, num_units=40)
    delta = (hypers['ymax']-hypers['ymin'])/2
    reynolds_stress = get_mixing_len_model(hypers['k'], delta)

    ## TRAINING: RETAU 1000
    retau=calc_retau(delta, hypers['dp_dx'], hypers['rho'], hypers['nu'])
    print('Training at Retau={}'.format(retau))
    pdenn1000 = Chanflow(num_units=hypers['num_units'], num_layers=hypers['num_layers'])
    losses1000 = pdenn1000.train(hypers['ymin'], hypers['ymax'],
                                   reynolds_stress,
                                   nu=hypers['nu'],
                                   dp_dx=hypers['dp_dx'],
                                   rho=hypers['rho'],
                                   batch_size=hypers['batch_size'],
                                   epochs=hypers['num_epochs'],
                                   lr=hypers['lr'],
                                   C=1)

    ## PLOT ##
    fig, ax = plt.subplots(1, 2, figsize=(20,10))
    # losses
    ax[0].plot(np.arange(len(losses1000)), losses1000, label='Retau={}'.format(retau))
    ax[0].set_title('Mean loss per epoch')
    ax[0].set_xlabel('epoch')
    ax[0].set_ylabel('mean loss')
    ax[0].legend()
    # preds
    y_space = torch.linspace(hypers['ymin'], hypers['ymax'], 1000).reshape(-1,1)
    preds1000 = pdenn1000(y_space).detach().numpy()
    ax[1].scatter(preds1000, y_space.detach().numpy(), alpha=1, s=1, label='Retau={}'.format(retau))
    ax[1].set_title('Predicted $<u>$')
    ax[1].set_ylabel('y')
    ax[1].set_xlabel('$<u>$')
    ax[1].legend()
    plt.show()
