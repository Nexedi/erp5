##############################################################################
#
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

try:
  from numpy import shape, array
except ImportError:
  from Numeric import shape, array

MODEL_HEAD = """
/* The number of samples.  */
param n, integer, > 0;

/* The number of resources.  */
param d, integer, > 0;

/* The set of samples.  */
set S := 1..n;

/* The set of resources.  */
set R := 1..d;

/* The query.  */
param q{i in R};

/* The samples.  */
param s{j in S, i in R};

/* The normal vector of a hyperplane.  */
var z{i in R};

/* The origin of a hyperplane.  */
var z0;

#display q;
#display s;

/* The objective.  */
maximize obj: sum {i in R} (z[i] * q[i]) - z0;

/* Constraints.  */
subject to c{j in S}: sum{i in R} (z[i] * s[j,i]) - z0, <= 0;
subject to c0: sum {i in R} (z[i] * q[i]) - z0, <= 1;

data;
"""

MODEL_TAIL="""
end;
"""

def writeModelFile(file, matrix, point):
    """
    Write an LP problem in MathProg.
    """
    n = shape(matrix)[0]
    d = shape(matrix)[1]
    
    file.write(MODEL_HEAD)
    file.write("param n := %d;\n" % n)
    file.write("param d := %d;\n" % d)
    
    file.write("param s\n:\t")
    def insertTab(x,y): return str(x)+"\t"+str(y)
    file.write(reduce(insertTab, range(1,d+1)))
    file.write("\t:=\n")
    for i in range(n):
        file.write(repr(i+1))
        file.write(reduce(insertTab, matrix[i], ""))
        file.write("\n")
    file.write(";\n")
        
    file.write("param q := ")
    def insertComma(x,y): return str(x)+','+str(y)
    def flatten(x): return str(x[0])+' '+str(x[1])
    file.write(reduce(insertComma,
                      map(flatten, map(None, range(1,d+1), point))))
    file.write(";\n")
    
    file.write(MODEL_TAIL)
    
def getOptimalValue(file):
    """
    Solve an LP problem described in MathProg language, and return
    the result of its objective function.
    This version uses GNU Linear Programming Kit.
    """
    import glpk
    lp = glpk.glp_lpx_read_model(file, None, None)
    try:
        glpk.glp_lpx_set_int_parm(lp, glpk.LPX_K_PRICE, 1)
        glpk.glp_lpx_set_int_parm(lp, glpk.LPX_K_PRESOL, 1)
        glpk.glp_lpx_set_int_parm(lp, glpk.LPX_K_BRANCH, 2)
        glpk.glp_lpx_set_int_parm(lp, glpk.LPX_K_BTRACK, 2)
        glpk.glp_lpx_set_real_parm(lp, glpk.LPX_K_TMLIM, 2000) # XXX
        ret = glpk.glp_lpx_simplex(lp)
        if ret != glpk.LPX_E_OK:
            raise RuntimeError, "The simplex method of GLPK failed"
        return glpk.glp_lpx_get_obj_val(lp)
    finally:
        glpk.glp_lpx_delete_prob(lp)

def solve(matrix, point):
    """
    Check if a point is inside a convex hull specified by a matrix.
    """
    import tempfile
    import os
    if shape(point)[0] != shape(matrix)[1]:
        raise TypeError, "The argument 'point' has a different number of dimensions from the capacity"
    mod_name = tempfile.mktemp(suffix='.mod')
    mod = file(mod_name, 'w')
    try:
        writeModelFile(mod, matrix, point)
        mod.close()
        obj = getOptimalValue(mod_name)
    finally:
        os.remove(mod_name)
    return obj <= 0

# This is a test.
if __name__ == '__main__':
    m = array([[ 0, 1, 2, 3, 4, 5],
               [10,11,12,13,14,15],
               [20,21,22,23,24,25],
               [30,31,32,33,34,35],
               [40,41,42,43,44,45],
               [50,51,52,53,54,55],
               [60,61,62,63,64,65],
               [70,71,72,73,74,75]])
    print m
    
    p = ([1,2,3,4,5,6])
    print p
    
    print solve(m, p)
