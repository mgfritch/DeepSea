
{% set node = salt.saltutil.runner('select.first', roles='storage') %}
{% set label = "ftof2" %}

Check environment {{ label }}:
  salt.state:
    - tgt: {{ node }}
    - sls: ceph.tests.migrate.check3
    - failhard: True

Remove OSDs {{ label }}:
  salt.state:
    - tgt: {{ node }}
    - sls: ceph.tests.migrate.remove_osds
       
Remove destroyed {{ label }}:
  salt.state:
    - tgt: {{ salt['master.minion']() }}
    - sls: ceph.remove.destroyed

Initialize OSDs {{ label }}:
  salt.state:
    - tgt: {{ node }}
    - sls: ceph.tests.migrate.init_osds
    - pillar: {{ salt.saltutil.runner('smoketests.pillar', minion=node, configuration='filestore') }}
       
Save reset checklist {{ label }}:
  salt.runner:
    - name: smoketests.checklist
    - arg:
        - {{ node }}
        - 'filestore'

Check reset OSDs {{ label }}:
  salt.state:
    - tgt: {{ node }}
    - sls: ceph.tests.migrate.check_osds
    - pillar: {{ salt.saltutil.runner('smoketests.pillar', minion=node, configuration='filestore') }}
    - failhard: True

Migrate {{ label }}:
  salt.state:
    - tgt: {{ node }}
    - sls: ceph.redeploy.osds
    - pillar: {{ salt.saltutil.runner('smoketests.pillar', minion=node, configuration='filestore2') }}

Save checklist {{ label }}:
  salt.runner:
    - name: smoketests.checklist
    - arg:
        - {{ node }}
        - 'filestore2'

Check OSDs {{ label }}:
  salt.state:
    - tgt: {{ node }}
    - sls: ceph.tests.migrate.check_osds
    - pillar: {{ salt.saltutil.runner('smoketests.pillar', minion=node, configuration='filestore2') }}
