#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import opengate as gate
import click
import json
import itk
import opengate.contrib.phantom_nema_iec_body as gate_iec

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--spacing", "-s", default=4, help="Spacing in mm")
@click.option("--output", "-o", required=True, help="output filename (.mhd)")
def go(output, spacing):
    # create the simulation
    sim = gate.Simulation()

    # shhhht !
    gate.log.setLevel(gate.NONE)

    # world
    m = gate.g4_units("m")
    sim.world.size = [1 * m, 1 * m, 1 * m]

    # add a iec phantom
    iec = gate_iec.add_phantom(sim)

    # initialize only (no source but no start).
    # initialization is needed because it builds the hierarchy of G4 volumes
    # that are needed by the "voxelize" function
    sim.initialize()

    # create an empty image with the size (extent) of the volume
    # add one pixel margin
    image = gate.create_image_with_volume_extent(
        sim, iec.name, spacing=[spacing, spacing, spacing], margin=1
    )
    info = gate.get_info_from_image(image)
    print(f"Image : {info.size} {info.spacing} {info.origin}")

    # voxelized a volume
    print("Starting voxelization ...")
    labels, image = gate.voxelize_volume(sim, iec.name, image)
    print(f"Output labels: ")
    gate.print_dic(labels)

    # write labels
    lf = output.replace(".mhd", ".json")
    outfile = open(lf, "w")
    json.dump(labels, outfile, indent=4)

    # write image
    print(f"Write image {output}")
    itk.imwrite(image, output)


# --------------------------------------------------------------------------
if __name__ == "__main__":
    go()
