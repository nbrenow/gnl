from multiprocessing import Pool

def caller(args):
    evolve, vec, tcur, tout = args
    return evolve(vec, tcur, tout)

class FilterDriver(object):

    def __init__(self, ensemble, evolver, analyzer, p=None):
        """
        Args:
            ensemble (2d array): (num state, num ensemble members)

            evolver: a callable that propagates each ensemble member with
                prototype `prior_member = evolver(ensemble_member, tcur, tout)`

            analyzer: a callable that analyzes each ensemble member given
                observations. It should have prototype:

                    analysis = analyzer(ensemble, obs)


        """
        self._ensemble = ensemble
        self._evolver= evolver
        self._analyzer = analyzer

        self._num_ensemble = ensemble.shape[1]
        self._processing_pool = p 

    def predict(self, tcur, tout):
        """Evolve ensemble members from tcur to tout."""
        
        if self._processing_pool is None:
            for i in range(self._num_ensemble):
                cur_member = self._ensemble[:,i]
                cur_member[:] = self._evolver(cur_member, tcur, tout)
        else:
            # ens = p.map(caller, ((self._evolver, self._ensemble[:,i], tcur, tout) 
            #                 for  i in range(self._num_ensemble)))
            ens = self._processing_pool.starmap(self._evolver, ((self._ensemble[:,i], tcur, tout) 
                            for  i in range(self._num_ensemble)))

            for i, en in enumerate(ens):
                self._ensemble[:,i] = en


    def analyze(self, obs):
        """Analysis step"""
        self._ensemble = self._analyzer(self._ensemble, obs)

    
    def iter(self, tout, obs):
        """Iterator for predict analyze loop"""

        nt = len(tout)
        ob = next(obs)

        # Assimilate Observations

        self.analyze(ob)
        yield self._ensemble

        for i in range(1,nt):
            print('Iteration {i} of {n}'.format(i=i, n=nt), end='\r')

            # Prediction
            self.predict(tout[i-1], tout[i])

            ob = next(obs)

            # Analysis
            self.analyze(ob)

            yield self._ensemble
