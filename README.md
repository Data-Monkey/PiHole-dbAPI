# PiHole-dbAPI
API to Enable / Disable groups in the PiHole gravity.db


I need to enable/disable groups via Home Assistant.


<B> This is not going to work, as we need to be able to run </B>


pihole restartdns reload-lists


<B>
Since that also requires access to the host we might as well update the DB via script. 
</B>
<br><p>

You could install the dbAPI on the PiHole host, then that would make it easier, but my PiHole is in a docker and I don't see myself writint a Dockerfile to add python and the API to the official docker.

