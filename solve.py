from ssc import current_location, snap_to_solver
from capture import poll_for_file
from astrometry import solver

"""get current view location, which can be used to narrow 
   down the plate solver's search task to a smaller set
   of indices"""
location = current_location()
print(f'location of current view: {location}')


"""poll the capture directory for the latest file for
which there is no prior solution"""
image_path = poll_for_file()
print(f'found file: {image_path}')


"""next, run the plate solver"""
solution = solver(image_path, location)
print(f'solution result: {solution}')


"""finally: if a solution was found, reset the stellarium view and
   rotation based on the solver results"""
#print(snap_to_solver())
