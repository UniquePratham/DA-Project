"""Ephemeral cloud infrastructure for BharatGov Access.

The observatory's research data is persistent. Its compute is not. Measurement
jobs are short-lived, so this package provisions a worker only when there is
work, runs the job, verifies the results reached central storage, and destroys
the worker.

Design rules, in priority order:

1. **Never destroy what we did not create.** Every instance carries an
   ownership tag. An instance without it is invisible to the reaper.
2. **Never lose research data.** An instance is not destroyed until the
   uploaded results have been verified against a checksum.
3. **Never spend without a ceiling.** Every provisioning decision is checked
   against a per-job and monthly budget before the API call is made.
4. **Never claim a domestic probe we do not have.** A country with no suitable
   region is marked unsupported rather than measured from a neighbour.

The provider interface is deliberately narrow so a second cloud can be added
without touching the lifecycle logic.
"""

from .budget import BudgetExceeded, BudgetGuard
from .cost import CostModel, InstancePrice
from .lifecycle import (
    InfrastructureManager,
    InstanceState,
    LifecycleError,
    OwnershipError,
)
from .provider import (
    CloudProvider,
    InstanceSpec,
    ProviderError,
    ProvisionedInstance,
    Region,
)
from .regions import CountryProbe, ProbeRegistry, ProbeStatus
from .vultr import VultrProvider

__all__ = [
    "BudgetExceeded",
    "BudgetGuard",
    "CloudProvider",
    "CostModel",
    "CountryProbe",
    "InfrastructureManager",
    "InstancePrice",
    "InstanceState",
    "InstanceSpec",
    "LifecycleError",
    "OwnershipError",
    "ProbeRegistry",
    "ProbeStatus",
    "ProviderError",
    "ProvisionedInstance",
    "Region",
    "VultrProvider",
]
