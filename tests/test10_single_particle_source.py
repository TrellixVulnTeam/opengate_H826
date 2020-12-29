#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gam
from scipy.spatial.transform import Rotation

gam.log.setLevel(gam.DEBUG)

# create the simulation
sim = gam.Simulation()
sim.set_g4_verbose(False)  # this play > 30% on the computation time !?
sim.set_g4_visualisation_flag(False)

# set random engine
sim.set_g4_random_engine("MersenneTwister", 123456)

# set the world size like in the Gate macro
m = gam.g4_units('m')
world = sim.get_volume_info('World')
world.size = [2 * m, 2 * m, 2 * m]

# add a simple volume
waterbox = sim.add_volume('Box', 'waterbox')
cm = gam.g4_units('cm')
waterbox.size = [40 * cm, 40 * cm, 40 * cm]
waterbox.translation = [0 * cm, 0 * cm, 0 * cm]
waterbox.material = 'G4_WATER'

# useful units
MeV = gam.g4_units('MeV')
keV = gam.g4_units('keV')
Bq = gam.g4_units('Bq')
deg = gam.g4_units('deg')
mm = gam.g4_units('mm')

# test sources
source = sim.add_source('Generic', 'source1')
source.particle = 'gamma'
source.activity = 10000 * Bq
source.position.type = 'sphere'
source.position.radius = 5 * mm
source.position.center = [-3 * cm, 30 * cm, -3 * cm]
source.direction.type = 'momentum'
source.direction.momentum = [0, -1, 0]
source.energy.type = 'mono'
source.energy.mono = 1 * MeV

source = sim.add_source('Generic', 'source2')
source.particle = 'proton'
source.activity = 10000 * Bq
source.position.type = 'disc'
source.position.radius = 5 * mm
source.position.center = [6 * cm, 5 * cm, -30 * cm]
# source.position.rotation = Rotation.from_euler('x', 45, degrees=True).as_matrix()
source.position.rotation = Rotation.identity().as_matrix()
source.direction.type = 'momentum'
source.direction.momentum = [0, 0, 1]
source.energy.type = 'gauss'
source.energy.mono = 140 * MeV
source.energy.sigma_gauss = 10 * MeV

source = sim.add_source('Generic', 'source3')
source.particle = 'proton'
source.activity = 10000 * Bq
source.position.type = 'box'
source.position.size = [4 * cm, 4 * cm, 4 * cm]
source.position.center = [8 * cm, 8 * cm, 30 * cm]
source.direction.type = 'focused'
source.direction.focus_point = [1 * cm, 2 * cm, 3 * cm]
source.energy.type = 'gauss'
source.energy.mono = 140 * MeV
source.energy.sigma_gauss = 10 * MeV

source = sim.add_source('Generic', 'source4')
source.particle = 'proton'
source.activity = 10000 * Bq
source.position.type = 'box'
source.position.size = [4 * cm, 4 * cm, 4 * cm]
source.position.center = [-3 * cm, -3 * cm, -3 * cm]
# source.position.rotation = Rotation.from_euler('x', 45, degrees=True).as_matrix()
source.position.rotation = Rotation.identity().as_matrix()
source.direction.type = 'iso'
source.energy.type = 'gauss'
source.energy.mono = 80 * MeV
source.energy.sigma_gauss = 1 * MeV

# actors
stats = sim.add_actor('SimulationStatisticsActor', 'Stats')

# src_info = sim.add_actor('SourceInfoActor', 'src_info')
# src_info.filename = 'output/sources.root'

dose = sim.add_actor('DoseActor', 'dose')
dose.save = 'output/test10-edep.mhd'
dose.attachedTo = 'waterbox'
dose.dimension = [50, 50, 50]
dose.spacing = [4 * mm, 4 * mm, 4 * mm]

# create G4 objects
sim.initialize()

# print after init
print(sim)
print('Simulation seed:', sim.seed)

# verbose
sim.apply_g4_command('/tracking/verbose 0')
# sim.g4_com("/run/verbose 2")
# sim.g4_com("/event/verbose 2")
# sim.g4_com("/tracking/verbose 1")

# start simulation
gam.source_log.setLevel(gam.RUN)
sim.start()

# get results
stats = sim.get_actor('Stats')
print(stats)

dose = sim.get_actor('dose')
print(dose)

# gate_test10
# Gate mac/main.mac
# Current version is two times slower :(
stats_ref = gam.read_stat_file('./gate_test10_generic_source/output/stat.txt')
print('-' * 80)
gam.assert_stats(stats, stats_ref, tolerance=0.05)
gam.assert_images('output/test10-edep.mhd', 'gate_test10_generic_source/output/output-Edep.mhd', tolerance=0.1)

gam.test_ok()