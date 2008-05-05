<tal:body xmlns:tal="http://xml.zope.org/namespaces/tal"
    xmlns:metal="http://xml.zope.org/namespaces/metal"
>Dear <tal:x replace="options/mto"/>,

<tal:x replace="user/getId"/> would like to thank you for
your interest in:
<tal:x replace="root/absolute_url"/>

<tal:x replace="options/message"/>

cheers,

The Web Team
</tal:body> 
