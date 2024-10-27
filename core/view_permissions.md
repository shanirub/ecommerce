**Background**

Group permissions are handled successfully using ``assign_permissions.py`` to set them, and ``GroupRequiredMixin`` to
enforce them.

orders present a new challenge in handling permissions: ownership.

**Problem**

Order items are always created in the context of an existing order.
Users in the ``customers`` group can manipulate only order items under their own orders.

So, before any operation is made on order items, the ownership of the respective order should be checked.



