#!/usr/bin/env python
"""
Script for generating synthetic datasets for single-sensor, multiple-time ICA.
"""

# --- Imports

# Standard library
import cmath
import math
from pathlib import Path
import glob
import os

# External packages
import numpy as np
from pydub import AudioSegment
from rich.console import Console
import typer
from tqdm import tqdm
import yaml


# --- Constants

# Typer arguments and options
_DATA_DIR = typer.Argument(..., help="directory containing audio files for sources")
_OUTPUT_DIR = typer.Argument(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "synthetic-single-sensor-multiple-time",
    ),
    help="directory that synthetic data is saved to",
)
_NUM_ACTIVE_SOURCES = typer.Option(
    3, "--num-active-sources", "-n", help="number of simultaneously active sources"
)
_NUM_TIME_POINTS = typer.Option(
    4, "--num-time-points", "-t", help="number of times points to generate data at"
)
_DIST_MAP = typer.Option(
    None,
    "--distance-map",
    "-m",
    help="YAML file containing distance of source for each audio file (units: meters)",
)
_MIN_DIST = typer.Option(
    400,
    "--min-dist",
    help="minimum allowable distance of sources from hydrophone (units: meters).",
)
_AVG_INIT_DIST = typer.Option(
    500,
    "--init-dist",
    "-i",
    help="average initial distance of sources from hydrophone (units: meters). "
    "Ignored if distance map is provided.",
)
_AVG_DELTA_DIST = typer.Option(
    250,
    "--delta-dist",
    "-d",
    help="average distance travelled by sources between time points (units: meters)",
)
_MIN_DELTA_DIST = typer.Option(
    200,
    "--min-delta-dist",
    help="minimum distance travelled by sources between time points (units: meters)",
)
_TEMPORAL_SHIFT = typer.Option(
    False,
    "--temporal-shift",
    "-S",
    help="apply a random temporal shift when combining sources",
)

# Error console
_ERROR_CONSOLE = Console(stderr=True)


# --- Main program


def main(
    data_dir: Path = _DATA_DIR,
    output_dir: Path = _OUTPUT_DIR,
    num_active_sources: int = _NUM_ACTIVE_SOURCES,
    num_time_points: int = _NUM_TIME_POINTS,
    distance_map_path: Path = _DIST_MAP,
    min_dist: float = _MIN_DIST,
    avg_init_dist: float = _AVG_INIT_DIST,
    avg_delta_dist: float = _AVG_DELTA_DIST,
    min_delta_dist: float = _MIN_DELTA_DIST,
    temporal_shift: bool = _TEMPORAL_SHIFT,
) -> None:
    """
    Generate synthetic datasets for single-sensor, multiple-time ICA.

    * The azimuth and heading of each source is modeled as a random variable uniformly
      distributed over the interval [0, 2 pi).

    * When distance data is not available, all distances (with units of meters) are
      modeled as random variables of the form D = max(avg_dist * Z, min_dist) where Z
      is a Gaussian random variable with mean 1 and standard deviation 0.1.

    * When `temporal-shift` is enabled, a random "temporal shift" is applied to the
      each source signal at each time point. The temporal shift is modeled as a random
      variable uniformly distributed over the interval [0, 1) seconds.
    """
    # --- Check arguments

    if not os.path.isdir(data_dir):
        _ERROR_CONSOLE.print(f"Error: Path to data '{data_dir}' does not exist.")
        raise typer.Abort()

    if num_active_sources <= 0:
        _ERROR_CONSOLE.print("Error: number of active sources must be positive.")
        raise typer.Abort()

    if num_time_points <= 0:
        _ERROR_CONSOLE.print("Error: number of time points must be positive.")
        raise typer.Abort()

    if distance_map_path is not None and not os.path.isfile(distance_map_path):
        _ERROR_CONSOLE.print(
            f"Error: Path to distance map '{distance_map_path}' does not exist."
        )
        raise typer.Abort()

    if min_dist <= 0:
        _ERROR_CONSOLE.print(
            "Error: minimum initial distance of sources from hydrophone must be "
            "positive."
        )
        raise typer.Abort()

    if avg_init_dist <= 0:
        _ERROR_CONSOLE.print(
            "Error: average initial distance of sources from hydrophone must be "
            "positive."
        )
        raise typer.Abort()

    if avg_delta_dist <= 0:
        _ERROR_CONSOLE.print(
            "Error: average distance travelled by sources between time points must "
            "be positive."
        )
        raise typer.Abort()

    if min_delta_dist <= 0:
        _ERROR_CONSOLE.print(
            "Error: minimum distance travelled by sources between time points must "
            "be positive."
        )
        raise typer.Abort()

    # --- Preparations

    # Emit status message
    print("Loading data...")

    # Read distance map
    if distance_map_path is not None:
        with open(distance_map_path, "r") as file_:
            distance_map = yaml.safe_load(file_)
    else:
        distance_map = None

    # Randomly select active sources
    num_sources = len(glob.glob(os.path.join(data_dir, "*.wav")))
    active_sources = np.random.choice(
        range(num_sources), size=num_active_sources, replace=False
    )

    # Load audio data for active sources
    audio_clips = []
    for i, file_path in enumerate(glob.glob(os.path.join(data_dir, "*.wav"))):
        if i in active_sources:
            # Load audio clip
            clip = AudioSegment.from_wav(file_path)

            # Get samples
            audio = clip.split_to_mono()[0]
            samples = audio.get_array_of_samples()

            # Convert samples to a NumPy array
            fp_arr = np.array(samples).T.astype(np.float32)
            # fp_arr /= np.iinfo(samples.typecode).max  # TODO: do we need this?

            # Get source distance
            if distance_map:
                distance = distance_map[os.path.basename(file_path)]
            else:
                distance = None

            # Get source distance
            audio_clips.append(
                {
                    "file": os.path.basename(file_path),
                    "distance": distance,
                    "data": fp_arr,
                    "frame_rate": audio.frame_rate,
                    "sample_width": audio.sample_width,
                    "num_samples": len(samples),
                }
            )

    # Check that frame rate and frame width are the same for all audio clips
    frame_rate = audio_clips[0]["frame_rate"]
    for clip in audio_clips:
        if clip["frame_rate"] != frame_rate:
            _ERROR_CONSOLE.print("Frame rates are not consistent across source clips.")
            raise typer.Abort

    sample_width = audio_clips[0]["sample_width"]
    for clip in audio_clips:
        if clip["sample_width"] != sample_width:
            _ERROR_CONSOLE.print("Frame widths are not consistent across source clips.")
            raise typer.Abort

    # Construct NumPy array containing clips of the same duration for active sources
    num_sources = len(audio_clips)
    num_samples = min(clip["num_samples"] for clip in audio_clips)
    audio_data = np.empty((num_samples, num_sources), dtype="float32")
    for i, clip in enumerate(audio_clips):
        audio_data[:, i] = clip["data"][0:num_samples]

    # --- Generate synthetic audio clips
    #
    #     Notes
    #     -----
    #     * Each source is assumed to start at random azimuth and travel with a random
    #       heading. The distance travelled by each source is a random variable with
    #       mean avg_delta_dist and standard deviation (0.1 * avg_delta_dist).

    print("Generating synthetic audio clips...")

    # ------ Preparations

    # Initialize array for source positions
    position = np.empty([num_time_points, num_active_sources], dtype=complex)

    # Initialize array for hydrophone data
    #
    # Note: the duration of the synthetic hydrophone clips is 60 seconds less
    #       than the source clips to accommodate the random temporal shifts of
    #       the source signals at different time points.
    num_pressure_samples = num_samples - frame_rate
    pressure = np.empty((num_pressure_samples, num_time_points))

    # ------ Generate source motion parameters

    delta_dist = avg_delta_dist * np.random.normal(
        loc=1.0, scale=0.1, size=num_active_sources
    )
    delta_dist[delta_dist < min_delta_dist] = min_delta_dist
    delta_azimuth = 2 * math.pi * np.random.random(size=num_active_sources)

    # Compute source deltas (represented as complex numbers)
    delta_pos = np.array(
        [cmath.rect(r, theta) for r, theta in zip(delta_dist, delta_azimuth)]
    )

    # ------ Generate initial positions

    if distance_map:
        r_init = np.array([clip["distance"] for clip in audio_clips])
    else:
        # Generate random initial distances from hydrophone
        r_init = avg_init_dist * np.random.normal(
            loc=1.0, scale=0.1, size=num_active_sources
        )
        r_init[r_init < min_dist] = min_dist

    # Generate random initial azimuth
    theta_init = 2 * math.pi * np.random.random(size=num_active_sources)

    # Compute positions (represented as complex numbers)
    position[0, :] = [cmath.rect(r, theta) for r, theta in zip(r_init, theta_init)]

    # ------ Generate positions at later times

    for i in range(1, num_time_points):
        position[i, :] = position[i - 1, :] + delta_pos
        while min(np.abs(position[i, :])) < min_dist:
            position[i, :] += delta_pos

    # ------ Compute sound amplitudes at the hydrophone

    # Compute pressure at initial time
    pressure[:, 0] = np.sum(audio_data[0:num_pressure_samples], axis=1)

    for i in range(1, num_time_points):
        # Generate offset for random temporal shift
        if temporal_shift:
            offset = int(frame_rate * np.random.random())
        else:
            offset = 0

        # Compute distances of sources from hydrophone
        r = np.abs(position[i, :])

        # Compute sound amplitudes
        amplitudes = np.diag(r_init / r)
        pressure[:, i] = np.sum(
            audio_data[offset : offset + num_pressure_samples] @ amplitudes, axis=1
        )

    # --- Save synthetic audio clips

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    print("Saving metadata...")

    source_files = [clip["file"] for clip in audio_clips]
    save_path = os.path.join(output_dir, f"sources.yaml")
    with open(save_path, "w") as file_:
        yaml.dump(source_files, file_)

    print("Saving synthetic audio clips...")

    for i in tqdm(range(num_time_points)):
        # Save pressures in CSV-format
        save_path = os.path.join(output_dir, f"t-{i}.csv")
        np.savetxt(save_path, pressure[:, i], delimiter=",")

        # Save as .wav file
        save_path = os.path.join(output_dir, f"t-{i}.wav")
        sample_array = np.array(np.round(pressure[:, i]), dtype="int16")
        audio = AudioSegment(
            sample_array,
            frame_rate=frame_rate,
            sample_width=sample_width,
            channels=1,
        )
        audio.export(save_path, format="wav")


# --- Run app

if __name__ == "__main__":
    typer.run(main)