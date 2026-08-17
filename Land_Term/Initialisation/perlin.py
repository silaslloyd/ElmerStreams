import numpy as np
import matplotlib.pyplot as plt
import re
import math


def _fade(t):
    """Perlin fade function."""
    return t * t * t * (t * (t * 6 - 15) + 10)


def _lerp(a, b, t):
    return a + t * (b - a)
import re
import math

def read_lua_value(filename, variable):
    values = {}

    safe_globals = {
        "__builtins__": {},
        "math": math,
    }

    with open(filename) as f:
        for line in f:
            # Remove comments
            line = line.split("--")[0].strip()

            if not line or "=" not in line:
                continue

            name, expr = map(str.strip, line.split("=", 1))

            # Lua -> Python
            expr = expr.replace("^", "**")
            expr = expr.rstrip(";").strip()

            try:
                values[name] = eval(expr, safe_globals, values)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to evaluate:\n{name} = {expr}"
                ) from e

    if variable not in values:
        raise ValueError(f"{variable} not found in {filename}")

    return values[variable]
def periodic_perlin_2d(nx, ny, Lx, Ly, wavelengths,
                       amplitudes=None,
                       seed=None):
    """
    Generate 2D Perlin noise that is

        - non-periodic in x
        - periodic in y

    Parameters
    ----------
    nx, ny : int
        Number of samples.

    Lx, Ly : float
        Physical dimensions of the domain.

    wavelengths : sequence of floats
        Wavelength of each octave in physical units.

    amplitudes : sequence of floats or None
        Amplitude of each octave.
        Defaults to 0.5**octave.

    seed : int or None
        Random seed.

    Returns
    -------
    noise : (ny, nx) ndarray
    """

    rng = np.random.default_rng(seed)

    if amplitudes is None:
        amplitudes = [0.5**i for i in range(len(wavelengths))]

    x = np.linspace(0, Lx, nx, endpoint=False)
    y = np.linspace(0, Ly, ny, endpoint=False)

    X, Y = np.meshgrid(x, y)

    noise = np.zeros_like(X)

    for wavelength, amp in zip(wavelengths, amplitudes):

        # Number of lattice cells
        gx = int(np.ceil(Lx / wavelength))
        gy = int(round(Ly / wavelength))

        # Require periodicity only in y
        if abs(gy * wavelength - Ly) > 1e-6:
            raise ValueError(
                f"Wavelength {wavelength} does not divide Ly={Ly}"
            )

        # Random unit gradient vectors
        # One extra column in x because x is not periodic
        theta = rng.uniform(0, 2*np.pi, size=(gy, gx + 1))
        gradients = np.stack(
            (np.cos(theta), np.sin(theta)),
            axis=-1
        )

        # Coordinates in lattice units
        xf = X / wavelength
        yf = Y / wavelength

        x0 = np.floor(xf).astype(int)
        y0 = np.floor(yf).astype(int)

        tx = xf - x0
        ty = yf - y0

        # Clamp x
        x0 = np.clip(x0, 0, gx - 1)
        x1 = x0 + 1

        # Wrap y
        y0 %= gy
        y1 = (y0 + 1) % gy

        # Gradient vectors
        g00 = gradients[y0, x0]
        g10 = gradients[y0, x1]
        g01 = gradients[y1, x0]
        g11 = gradients[y1, x1]

        # Dot products
        n00 = g00[..., 0] * tx       + g00[..., 1] * ty
        n10 = g10[..., 0] * (tx - 1) + g10[..., 1] * ty
        n01 = g01[..., 0] * tx       + g01[..., 1] * (ty - 1)
        n11 = g11[..., 0] * (tx - 1) + g11[..., 1] * (ty - 1)

        # Smooth interpolation
        u = _fade(tx)
        v = _fade(ty)

        nx0 = _lerp(n00, n10, u)
        nx1 = _lerp(n01, n11, u)

        octave = _lerp(nx0, nx1, v)

        noise += amp * octave

    # Normalize to [-1, 1]
    noise /= np.max(np.abs(noise))

    return noise

# =============================================================================
# Parameters
# =============================================================================

lua_file = "../parameters.lua"

# Uncomment these if you want to read from the Lua file
Lx = float(read_lua_value(lua_file, "L"))
Ly = float(read_lua_value(lua_file, "W"))

nx = int(read_lua_value(lua_file, "Nx"))
ny = int(read_lua_value(lua_file, "Ny"))

k = 40
wavelength = Ly / k
print(nx)
print(ny)
noise = periodic_perlin_2d(
    nx=nx,
    ny=ny,
    Lx=Lx,
    Ly=Ly,
    wavelengths=[wavelength],
    amplitudes=[1.0],
    seed=1
)

# =============================================================================
# Save to file
# x increases first, then y
# =============================================================================

x = np.linspace(0, Lx, noise.shape[1])
y = np.linspace(0, Ly, noise.shape[0])

X, Y = np.meshgrid(x, y)

data = np.column_stack((
    X.ravel(order="C"),
    Y.ravel(order="C"),
    noise.ravel(order="C")
))

np.savetxt(
    "perlin_noise.dat",
    data,
    fmt="%.6f %.6f %.8f"
)

# =============================================================================
# Plot (optional)
# =============================================================================

plt.figure(figsize=(12, 4))
plt.imshow(
    noise,
    origin="lower",
    extent=[0, Lx, 0, Ly],
    cmap="terrain",
    aspect="auto"
)
#plt.colorbar(label="Noise")
#plt.xlabel("x")
#plt.ylabel("y")
#plt.tight_layout()
#plt.show()
