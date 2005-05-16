# TODO: FHS compliance (/var/nullmailer -> /var/lib/nullmailer)
Summary:	Simple relay-only mail transport agent
Summary(pl):	Prosty, wy³±cznie przekazuj±cy MTA
Name:		nullmailer
Version:	1.00
Release:	0.1
License:	GPL
Group:		Networking/Daemons
Source0:	http://untroubled.org/nullmailer/%{name}-%{version}.tar.gz
# Source0-md5:	ead32b3543ef652891edf3856ec759dd
Patch0:		%{name}-time.patch
URL:		http://untroubled.org/nullmailer/
BuildRequires:	libstdc++-devel
BuildRequires:	rpmbuild(macros) >= 1.202
Prereq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Provides:	group(nullmail)
Provides:	smtpdaemon
Provides:	user(nullmail)
Obsoletes:	courier
Obsoletes:	exim
Obsoletes:	masqmail
Obsoletes:	omta
Obsoletes:	postfix
Obsoletes:	qmail
Obsoletes:	sendmail
Obsoletes:	sendmail-cf
Obsoletes:	sendmail-doc
Obsoletes:	smail
Obsoletes:	smtpdaemon
Obsoletes:	ssmtp
Obsoletes:	zmailer
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Nullmailer is a mail transport agent designed to only relay all its
messages through a fixed set of "upstream" hosts. It is also designed
to be secure.

%description -l pl
Nullmailer to MTA przeznaczony tylko do przekazywania wszystkich
wiadomo¶ci do ustalonej listy "nadrzêdnych" serwerów. Zosta³
zaprojektowany tak¿e z my¶l± o bezpieczeñstwie.

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

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

ln -s ../sbin/sendmail $RPM_BUILD_ROOT%{_libdir}/sendmail
install scripts/nullmailer.run $RPM_BUILD_ROOT/var/nullmailer/service/run
install scripts/nullmailer-log.run $RPM_BUILD_ROOT/var/nullmailer/service/log/run

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 62 nullmail
%useradd -u 62 -d /var/lock/svc/nullmailer -s /bin/false -c "NullMailer User" -g nullmail nullmail

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
	%userremove nullmail
	%groupremove nullmail
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS BUGS ChangeLog NEWS README TODO YEAR2000
%dir %{_sysconfdir}/nullmailer
%attr(4755,nullmail,nullmail) %{_bindir}/mailq
%attr(755,root,root) %{_bindir}/nullmailer-inject
%{_libdir}/sendmail
%dir %{_libdir}/nullmailer
%{_libdir}/nullmailer/*
%{_mandir}/man?/*
%attr(4755,nullmail,nullmail) %{_sbindir}/nullmailer-queue
%attr(755,root,root) %{_sbindir}/nullmailer-send
%attr(755,root,root) %{_sbindir}/sendmail
/var/log/nullmailer
%attr(740,nullmail,root) /var/nullmailer
