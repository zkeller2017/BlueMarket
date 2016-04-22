#!/usr/bin/perl

require "common.pl";

# -----------------------------------------------
# Local variables

# FQDN of LDAP servers
$dc1 = "ldap1.pingry.org";
$dc2 = "ldap2.pingry.org";

# LDAP container to search
# The syntax is CN=Users,dc=example,dc=com
$searchbase = "ou=Users,dc=pingry,dc=org";

# LDAP domain for user principal name
$ldapdomain = "pingry.org";

# -----------------------------------------------
# Main body of code

$username = $cgi->param('username');
$password = $cgi->param('password');

if (defined(checkLDAP($username, $password)))
{
  $select = $dbh->prepare("select firstname,lastname
    from Students
    where username=?");

  $select->execute($username);

#  if (@resultsql = $select->fetchrow_array())
if (1)
  {
    $session->param('firstname',$resultsql[0]);
    $session->param('lastname',$resultsql[1]);
    $session->param('_IS_LOGGED_IN','1');
    $redirect =  "$cgiurl/main.cgi";
  }
  else
  {
    $session->param('_IS_LOGGED_IN','0');
    $redirect =  "$cgiurl/invalid.cgi";
  }

  print $cgi->redirect(-cookie=>$cookie, -uri=>$redirect );

  $select->finish;
  $dbh->disconnect();
}
else
{
  $session->clear(["_IS_LOGGED_IN"]);
  print $cgi->header();
  $template->define(main => "index.html");
  $template->parse(main => "main");
  $template->print();
}

exit;

# -----------------------------------------------
# Subroutines
sub checkLDAP
{
  my ($user, $passwd) = @_;

  use Net::LDAP;
  use Net::LDAP::Control::Paged;
  use Net::LDAP::Constant ( "LDAP_CONTROL_PAGED" );

  # Connecting to Active Directory domain controllers
  $noldapserver=0;
  $ldap = Net::LDAP->new($dc1) or
    $noldapserver=1;

  if ($noldapserver == 1)
  {
    $ldap = Net::LDAP->new($dc2) or
      die "Error connecting to specified domain controllers $@ \n";
  }

  $mesg = $ldap->bind (
    dn => "$user\@$ldapdomain",
    password => $passwd);

  if ($mesg->code())
  {
    return;
#    die ("error:", $mesg->code(),"\n","error name: ",$mesg->error_name(),
#      "\n", "error text: ",$mesg->error_text(),"\n");
  }

  # How many LDAP query results to grab for each paged round
  # Set to under 1000 for Active Directory
  $page = Net::LDAP::Control::Paged->new( size => 990 );

  @args = ( base     => $searchbase,
        filter => "(&
                  (objectCategory=person)
                  (objectClass=user)
                  (sAMAccountName=$user)
                )",
        control  => [ $page ],
  );

  my $cookie;

  while(1)
  {
    # Perform search
    my $mesg = $ldap->search( @args );
    foreach my $entry ( $mesg->entries )
    {
      ($dept) = $entry->get_value( "distinguishedName" ) =~
        m/,OU=([^,]+),/;
#      $dept =~ tr/a-z/A-Z/;
    }

    # Only continue on LDAP_SUCCESS
    $mesg->code and last;

    # Get cookie from paged control
    my($resp)  = $mesg->control( LDAP_CONTROL_PAGED ) or last;
    $cookie    = $resp->cookie or last;

    # Set cookie in paged control
    $page->cookie($cookie);
  }

  if ($cookie)
  {
    # We had an abnormal exit, so let the server know we do not want any more
    $page->cookie($cookie);
    $page->size(0);
    $ldap->search( @args );

    # Also would be a good idea to die unhappily and inform OP at this point
    die("LDAP query unsuccessful");
  }

  return $dept;
}

