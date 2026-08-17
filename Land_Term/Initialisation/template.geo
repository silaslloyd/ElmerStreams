// footprint_symmetric.geo

// Same rectangular footprint mesh as footprint_original.geo, but with a

// GUARANTEED perfect mirror symmetry about the mid-line y = W/2.

//

// Strategy: the rectangle is split at y = W/2 into a bottom half [0,W/2] and a

// top half [W/2,W]. The two halves SHARE the mid-line curve (Line 3) so the

// mesh is conforming on the symmetry axis. The bottom half is meshed as the

// "master"; the top half is forced to be an affine-reflected copy of it via

// a Periodic Surface constraint. Reflection about y = W/2 is (x,y,z)->(x,W-y,z),

// which maps the master (bottom) exactly onto the slave (top). Because the

// background size field depends only on x, it is invariant under this

// reflection, so the mirrored mesh respects the intended density everywhere.

Mesh.Algorithm = 5;

Mesh.MeshSizeFromPoints = 10000;

Mesh.MeshSizeFromCurvature = 10000;

Mesh.MeshSizeExtendFromBoundary = 10000;

Mesh.MeshSizeMin = 100;

Mesh.MeshSizeMax = 10000;

L={L};

GL={GL};

W={W};


resb={BoundaryRes};

resgl = {GLRes};

// --- Geometry: split at the symmetry line y = W/2 -------------------------

// Bottom-half corners

Point(1) = {0, 0,   0, resb};   // bottom-left  (y = 0)

Point(2) = {L, 0,   0, resb};   // bottom-right (y = 0)

Point(3) = {L, W/2, 0, resb};   // mid-right    (y = W/2)

Point(4) = {0, W/2, 0, resb};   // mid-left     (y = W/2)

// Top-half extra corners

Point(5) = {L, W,   0, resb};   // top-right    (y = W)

Point(6) = {0, W,   0, resb};   // top-left     (y = W)

// Bottom-half edges

Line(1) = {1, 2};   // y = 0

Line(2) = {2, 3};   // right, lower (x = L)

Line(3) = {3, 4};   // SHARED mid-line at y = W/2 (symmetry axis)

Line(4) = {4, 1};   // left, lower  (x = 0)

// Top-half edges (mid-line reused as Line 3)

Line(5) = {3, 5};   // right, upper (x = L)

Line(6) = {5, 6};   // y = W

Line(7) = {6, 4};   // left, upper  (x = 0)

// Bottom half = MASTER surface

Curve Loop(1) = {1, 2, 3, 4};

Plane Surface(100) = {1};

// Top half = SLAVE surface (shares Line 3 with the master)

Curve Loop(2) = {-3, 5, 6, 7};

Plane Surface(200) = {2};

// --- Force the top half to be the mirror image of the bottom half ---------

// Reflection about y = W/2:  x'=x, y'=W-y, z'=z

// 4x4 affine matrix, row-major.

Periodic Surface {200} = {100} Affine {1, 0, 0, 0,

                                        0, -1, 0, W,

                                        0, 0, 1, 0,

                                        0, 0, 0, 1};

// --- Background size field (identical to the original; depends on x only) --

Field[1] = MathEval;

Field[1].F =

"{GLRes} + (-1000)*exp(-((x-(0.75*{L}))^6)/(((0.05*{L}))^6))  +  (4000)*exp(-((x-(0))^6)/((({L}/10))^6))";

Background Field = 1;

Physical Surface(21) = {100,200};


Physical Curve(22) = {4,7};   // x = 0 (left)
Physical Curve(23) = {2,5};   // x = L (right)
Physical Curve(24) = {1};     // y = 0 (bottom)
Physical Curve(25) = {6};     // y = W (top)
