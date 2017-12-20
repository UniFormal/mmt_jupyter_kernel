from ipykernel.kernelapp import IPKernelApp
from . import MMTKernel

IPKernelApp.launch_instance(kernel_class=MMTKernel)
