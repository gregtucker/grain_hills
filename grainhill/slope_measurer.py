#!/usr/bin/env python2
# -*- cpding: utf-8 -*-
"""
slope_measurer.py: GrainHill module that retrieves the (x, z) coordinates of
surface bedrock cells in a cellular hillslope cross-section.

Created Wed Apr 18 14:48 2018

@author: SiccarPoint
"""

import numpy as np


def row_col_to_id(row, col, num_cols):
    """Return ID for node at given row and column.

    Examples
    --------
    >>> row_col_to_id(0, 1, 8)
    4
    >>> row_col_to_id(0, 6, 8)
    3
    >>> row_col_to_id(0, 1, 5)
    3
    >>> row_col_to_id(2, 3, 5)
    14
    """
    return row * num_cols + col // 2 + (col % 2) * ((num_cols + 1) // 2)


class SlopeMeasurer(object):
    """SlopeMeasurer: extracts nodes at the bedrock-air or regolith-air
    surface, and fits to this data according to user choices."""

    def __init__(self, grain_hill_model, pick_only_rock=True, rock_id=8,
                 static_regolith_id=7, air_id=0):
        """Initialise a SlopeMeasurer.

        If pick_only_rock, SlopeMeasurer will track the bedrock-air interface.
        If False, it will track the regolith-air interface.
        """
        self.model = grain_hill_model
        self.grid = grain_hill_model.ca.grid
        self.rock_id = rock_id
        self.air_id = air_id
        self.reg_id = static_regolith_id
        self.bedrock_surface = []

        lsd = self.model.ca.link_state_dict
        if pick_only_rock:
            rock_options = (rock_id, )
        else:
            rock_options = (rock_id, static_regolith_id)
        state_options = lsd.keys()
        airrock_states = []
        self.rockend = []
        for opt in state_options:
            if opt[0] in rock_options:
                if opt[1] is air_id:
                    airrock_states.append(opt)
                    self.rockend.append(0)
            elif opt[0] is air_id:
                if opt[1] in rock_options:
                    airrock_states.append(opt)
                    self.rockend.append(1)
        self.airrock_link_state_codes = [
            lsd[state] for state in airrock_states]

    def pick_rock_surface(self):
        """Identify nodes at the rock-air (or regolith-air, as appropriate)
        interface, and return the IDs of the rock/regolith nodes as an array.

        Examples
        --------
        >>> from grainhill import GrainHill
        >>> gh = GrainHill((5, 7), show_plots=False)
        >>> gh.ca.node_state[:18] = 8
        >>> gh.ca.node_state[19:21] = 7  # a partial soil mantle
        >>> gh.ca.node_state[22] = 8  # a rock nubbin
        >>> gh.ca.assign_link_states_from_node_types()
        >>> sm = SlopeMeasurer(gh)
        >>> sm.pick_rock_surface()
        array([11, 14, 15, 16, 22])
        >>> sm = SlopeMeasurer(gh, False)
        >>> sm.pick_rock_surface()
        array([11, 14, 15, 16, 19, 20, 22])
        """
        # find the links that are air-rock (or air-reg)
        rock_nodes = []
        for statecode, end in zip(self.airrock_link_state_codes, self.rockend):
            is_airrock = self.model.ca.link_state == statecode
            if end is 0:
                rock_nodes.extend(self.grid.node_at_link_tail[is_airrock])
            else:
                rock_nodes.extend(self.grid.node_at_link_head[is_airrock])
        self.exposed_surface = np.array(list(set(rock_nodes)))
        self.exposed_surface.sort()

        return self.exposed_surface

    def fit_straight_line_to_surface(self, min_x=None, max_x=None,
                                     first_nodes=None):
        """
        Fit a straight line to a surface which has already been found with
        pick_rock_surface(). If min_x==float, only take nodes positive from
        that coordinate. If max_x==float, only take nodes negative from
        that coordinate. If first_nodes==int, take the first int nodes (by node
        id) only. These options can all be combined, and will give the minimum
        possible number of nodes.

        Returns array([m, c]), where z = m*x + c (i.e., m is the gradient).
        Also saves the internal params m, c, S ("slope", +ve m), and dip_angle
        (from horizontal, in **positive degrees**).

        Examples
        --------
        >>> from grainhill import GrainHill
        >>> gh = GrainHill((4, 8), show_plots=False)
        >>> gh.ca.node_state[:16] = 8
        >>> gh.ca.node_state[17] = 8  # make the surface imperfect
        >>> gh.ca.assign_link_states_from_node_types()
        >>> sm = SlopeMeasurer(gh)
        >>> sm.pick_rock_surface()
        array([10, 11, 12, 13, 14, 15, 17])
        >>> m_and_c = sm.fit_straight_line_to_surface()
        >>> np.round(m_and_c, 4)[0]  # the gradient
        -0.082
        >>> np.round(sm.S, 4)
        0.082
        >>> np.round(sm.dip_angle, 3)
        4.71

        ...and without the bump...

        >>> m_and_c = sm.fit_straight_line_to_surface(min_x=1.8)
        >>> sm.nodes_fitted
        array([10, 11, 13, 14, 15])
        >>> np.isclose(m_and_c[0], 0.)
        True

        Then an alternative way:

        >>> m_and_c = sm.fit_straight_line_to_surface(min_x=1.7,
        ...                                           first_nodes=5)
        >>> sm.nodes_fitted  # 17 gets chopped by first_nodes==5
        array([10, 11, 13, 14, 15])
        >>> np.isclose(sm.dip_angle, 0.)
        True
        """
        surface_x = self.grid.node_x[self.exposed_surface]
        surface_z = self.grid.node_y[self.exposed_surface]
        cond = np.ones(len(surface_x), dtype=bool)
        if min_x is not None:
            if max_x is not None:
                cond = np.logical_and(surface_x > min_x, surface_x < max_x)
            else:
                cond = surface_x > min_x
            surface_x = surface_x[cond]
            surface_z = surface_z[cond]
        elif max_x is not None:
            cond = surface_x < max_x
            surface_x = surface_x[cond]
            surface_z = surface_z[cond]

        # now see if we need to truncate:
        if first_nodes is not None:
            surface_x = surface_x[:first_nodes]
            surface_z = surface_z[:first_nodes]
            cond = np.where(cond)[0]
            cond = cond[:first_nodes]

        # save the nodes we used
        self.nodes_fitted = self.exposed_surface[cond]

        # fit the line
        polyparams = np.polyfit(surface_x, surface_z, 1)
        self.m = polyparams[0]
        self.c = polyparams[1]
        self.S = np.abs(self.m)
        self.dip_angle = np.arctan(self.S)*180./np.pi

        return polyparams
