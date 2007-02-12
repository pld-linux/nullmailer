# TODO: FHS compliance (/var/nullmailer -> /var/lib/nullmailer)
Summary:	Simple relay-only mail transport agent
Summary(pl.UTF-8):   Prosty, wyłącznie przekazujący MTA
Name:		nullmailer
Version:	1.02
Release:	2
License:	GPL
Group:		Networking/Daemons
Source0:	http://untroubled.org/nullmailer/%{name}-%{version}.tar.gz
# Source0-md5:	848d5c1f41a78e6897aeeb615e484d38
Source1:	%{name}.init
Patch0:		%{name}-FHS.patch
URL:		http://untroubled.org/nullmailer/
BuildRequires:	libstdc++-devel
BuildRequires:	rpmbuild(macros) >= 1.202
Requires:	rc-scripts
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

%description -l pl.UTF-8
Nullmailer to MTA przeznaczony tylko do przekazywania wszystkich
wiadomości do ustalonej listy "nadrzędnych" serwerów. Został
zaprojektowany także z myślą o bezpieczeństwie.

%prep
%setup -q
%patch0 -p1

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

ln -s ../sbin/sendmail $RPM_BUILD_ROOT%{_libdir}/sendmail

install %SOURCE1 $RPM_BUILD_ROOT/etc/rc.d/init.d/nullmailer
:>$RPM_BUILD_ROOT%{_sysconfdir}/nullmailer/me
:>$RPM_BUILD_ROOT%{_sysconfdir}/nullmailer/defaultdomain
:>$RPM_BUILD_ROOT%{_sysconfdir}/nullmailer/remotes


%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 62 nullmail
%useradd -u 62 -d /var/spool/nullmailer -s /bin/false -c "NullMailer User" -g nullmail nullmail

%post
if [ ! -s %{_sysconfdir}/nullmailer/me ]; then
	/bin/hostname --fqdn >%{_sysconfdir}/nullmailer/me
fi
if [ ! -s %{_sysconfdir}/nullmailer/defaultdomain ]; then
	/bin/hostname --domain >%{_sysconfdir}/nullmailer/defaultdomain
fi
/sbin/chkconfig --add nullmailer
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
%attr(754,root,root) /etc/rc.d/init.d/nullmailer
%dir %{_sysconfdir}/nullmailer
%ghost %{_sysconfdir}/nullmailer/defaultdomain
%ghost %{_sysconfdir}/nullmailer/me
%ghost %{_sysconfdir}/nullmailer/remotes
%attr(4755,nullmail,nullmail) %{_bindir}/mailq
%attr(755,root,root) %{_bindir}/nullmailer-inject
%{_libdir}/sendmail
%dir %{_libdir}/nullmailer
%attr(755,root,root) %{_libdir}/nullmailer/qmqp
%attr(755,root,root) %{_libdir}/nullmailer/smtp
%attr(4755,nullmail,nullmail) %{_sbindir}/nullmailer-queue
%attr(755,root,root) %{_sbindir}/nullmailer-send
%attr(755,root,root) %{_sbindir}/sendmail
%attr(740,nullmail,root) /var/spool/nullmailer
%{_mandir}/man?/*
