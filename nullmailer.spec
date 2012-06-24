Name:		nullmailer
Summary:	Simple relay-only mail transport agent
Version:	1.00RC5
Release:	0.1
License:	GPL
Group:		Networking/Daemons
Source0:	http://em.ca/~bruceg/nullmailer/archive/%{version}/%{name}-%{version}.tar.gz
Patch0:		%{name}-time.patch
URL:		http://em.ca/~bruceg/nullmailer/
Prereq:		rc-scripts
Provides:       smtpdaemon
Obsoletes:      smtpdaemon
Obsoletes:      exim
Obsoletes:      masqmail
Obsoletes:      omta
Obsoletes:	postfix
Obsoletes:      qmail
Obsoletes:      sendmail
Obsoletes:      sendmail-cf
Obsoletes:      sendmail-doc
Obsoletes:      smail
Obsoletes:      zmailer
Requires(pre):  /usr/sbin/useradd
Requires(pre):  /usr/sbin/groupadd
Requires(pre):  /usr/bin/getgid
Requires(pre):  /bin/id
Requires(post,preun):/sbin/chkconfig
Requires(postun):       /usr/sbin/userdel
Requires(postun):       /usr/sbin/groupdel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Nullmailer is a mail transport agent designed to only relay all its
messages through a fixed set of "upstream" hosts. It is also designed
to be secure.

%prep
%setup -q
%patch0

%build
%configure2_13

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/{usr/lib,etc/rc.d/init.d}
install -d $RPM_BUILD_ROOT/var/{nullmailer/service/log,log/nullmailer}

%{__make} DESTDIR=$RPM_BUILD_ROOT install
ln -s ../sbin/sendmail $RPM_BUILD_ROOT%{_libdir}/sendmail
install scripts/nullmailer.run $RPM_BUILD_ROOT/var/nullmailer/service/run
install scripts/nullmailer-log.run $RPM_BUILD_ROOT/var/nullmailer/service/log/run

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`/usr/bin/getgid nullmail`" ]; then
	if [ "`getgid nullmailer`" != "62" ]; then
		echo "Warning: group nullmail haven't gid=62. Correct this before installing nullmailer" 1>&2
		exit 1
        fi
else
	/usr/sbin/groupadd -g 62 -r -f nullmail
fi

if [ -n "`/bin/id -u nullmail 2>/dev/null`" ]; then
	if [ "`/bin/id -u nullmail`" != "62" ]; then
		echo "Warning: user nullmail haven't uid=62. Correct this before installing nullmailer"
1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 62 -r -d /var/lock/svc/nullmailer -s /bin/false -c "NullMailer User" -g nullmail nullmail 1>&2
fi

%post
/sbin/chkconfig --add postfix
if [ -f /var/lock/subsys/nullmailer ]; then
        /etc/rc.d/init.d/nullmailer restart >&2
else
        echo "Run \"/etc/rc.d/init.d/nullmailer start\" to start nullmailer daemon." >&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/nullmailer ]; then
		/etc/rc.d/init.d/nullmailer stop >&2
	fi
	/sbin/chkconfig --del nullmailer
fi

%postun
if [ "$1" = 0 ]; then
	# post-erase instructions
	/usr/sbin/userdel nullmail 2>/dev/null
	/usr/sbin/groupdel nullmail 2>/dev/null
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS BUGS ChangeLog NEWS README TODO YEAR2000
%dir %{_sysconfdir}/nullmailer
%attr(04711,nullmail,nullmail) %{_bindir}/mailq
%attr(755,root,root) %{_bindir}/nullmailer-inject
%{_libdir}/sendmail
%dir %{_libdir}/nullmailer
%{_libdir}/nullmailer/*
%{_mandir}/man?/*
%attr(04711,nullmail,nullmail) %{_sbindir}/nullmailer-queue
%attr(755,root,root) %{_sbindir}/nullmailer-send
%attr(755,root,root) %{_sbindir}/sendmail
%dir /var/log/nullmailer
/var/nullmailer
