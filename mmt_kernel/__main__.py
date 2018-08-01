from ipykernel.kernelapp import IPKernelApp
from . import JupyterKernel

IPKernelApp.launch_instance(kernel_class=JupyterKernel)
