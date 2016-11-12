#!/usr/bin/env python
# :noTabs=true:
# (c) Copyright Rosetta Commons Member Institutions.
# (c) This file is part of the Rosetta software suite and is made available under license.
# (c) The Rosetta software is developed by the contributing members of the Rosetta Commons.
# (c) For more information, see http://www.rosettacommons.org. Questions about this can be
# (c) addressed to University of Washington UW TechTransfer, email: license@u.washington.edu.

## @author Sergey Lyskov
## @brief  Demo for PyRosetta sub classing

import sys

import rosetta
import rosetta.core.pose
import rosetta.core.scoring
import rosetta.core.scoring.methods

rosetta.init()

# Mover sub-classing -----------------------------------
class My_New_Mover(rosetta.protocols.moves.Mover):
    def __init__(self):
        print 'My_New_Mover.__init__...'
        rosetta.protocols.moves.Mover.__init__(self)

    def get_name(self): return 'My_New_Mover'

    def apply(self, p):
        if isinstance(p, rosetta.core.pose.PoseAP):
            print 'Got rosetta.core.pose.PoseAP!'
            p = p.get()

        print 'This My_New_Mover apply...'
        p.set_phi(1, p.phi(1)+1)


new_mover = My_New_Mover()

pose = rosetta.pose_from_pdb("test/data/test_in.pdb")
sf_new = rosetta.core.scoring.ScoreFunction()

seq = rosetta.protocols.moves.SequenceMover()
seq.add_mover( new_mover )

minmover = rosetta.protocols.simple_moves.MinMover()

old_phi = pose.phi(1)
seq.apply(pose)
print 'Old phi=%s, new phi=%s' % (old_phi, pose.phi(1))
if pose.phi(1) == old_phi : sys.exit(1)




# rosetta.core.scoring.methods.ContextIndependentOneBodyEnergy sub-classing -----------------------------------

# Making energy creator class by hand, this is for demo purpose only, in real programm use class decorator instead (see below)
_mem_ = []
class MyNewCI1B_Creator(rosetta.core.scoring.methods.EnergyMethodCreator):
    def __init__(self):
        rosetta.core.scoring.methods.EnergyMethodCreator.__init__(self)

    def create_energy_method(self, energy_method_options):
        e = MyNewCI1B()
        _mem_.append(e)
        return e

    def score_types_for_method(self):
        sts = rosetta.core.vector1_ScoreType();  sts.append( rosetta.core.scoring.PyRosettaEnergy_last )
        return sts


class MyNewCI1B(rosetta.core.scoring.methods.ContextIndependentOneBodyEnergy):
    def __init__(self):
        print 'MyNewCI1B::__init__!'
        rosetta.core.scoring.methods.ContextIndependentOneBodyEnergy.__init__(self, MyNewCI1B_Creator() )

    def residue_energy(self, rsd, pose, emap):
        #print 'residue_energy:', type(emap)
        emap.get().set(rosetta.core.scoring.PyRosettaEnergy_last, 2.0)


    def clone(self): return MyNewCI1B();

    def version(self): return 1

    def indicate_required_context_graphs(self, v): pass


b = MyNewCI1B_Creator()
rosetta.core.scoring.methods.PyEnergyMethodRegistrator( b )


sf_new = rosetta.core.scoring.ScoreFunction()
sf_new.set_weight(rosetta.core.scoring.PyRosettaEnergy_last, 1)
print '---------------------------------------------'
print 'Score:', sf_new.score(pose)