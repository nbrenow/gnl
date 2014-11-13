from scipy.linalg import solve
from ..util import vdot


def kalman_filter(prior_mean, prior_var, obs, obs_var, obs_mat):
    """Kalman filter function

    Args:
        prior_mean: (n,) array_like
        prior_var: (n, n) prior noise covariance
        obs: (k,) observations
        obs_var: (k,k) the observation noise covariance
        obs_mat: (k,n) The linear observation operator

    """

    # H Sigma H' + R
    tmp1 = vdot(obs_mat, prior_var, obs_mat.T) + obs_var

    inov = obs - vdot(obs_mat, prior_mean)
    post_mean = prior_mean + vdot(prior_var, obs_mat.T, solve(imp1, inov))
    
    post_var  = prior_var - vdot(prior_var, obs_mat.T, 
                                 solve(tmp1, vdot(obs_mat, prior_var)))


    return post_mean, post_var


