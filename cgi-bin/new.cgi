#!/usr/bin/perl

require "common.pl";

use CGI::Ajax;
my $ajax = CGI::Ajax->new(
	loadBook => \&loadBook
);

# -----------------------------------------------

if ($session->param("_IS_LOGGED_IN"))
{
#  print $cgi->header(-cookie=>$cookie );
  my ($lname, $fname) = lookupStudent($session->param('username'));
  my ($course) = lookupCourse($cgi->param('COURSE'));

  $template->define(main => "entry.html");
  $template->assign(CONTENTS => $contents);
  $template->assign(FIRSTNAME => uc($fname));
  $template->assign(LASTNAME => uc($lname));
  $template->assign(COURSE => $course);
  $template->assign(COURSENUM => $cgi->param('COURSE'));
  $template->assign(RECNUM => 'NEW');
  $template->assign(STATUSA => 'CHECKED');
  $template->assign(STATUSI => '');
  $template->assign(ISBN => '');
  $template->assign(CONDITION => '');
  $template->assign(COMMENTS => '');
}
else
{
  $session->clear(["_IS_LOGGED_IN"]);
  print $cgi->header();
  $template->define(main => "index.html");
}

$html = &showHTML;
print $ajax->build_html( $cgi, $$html );


exit;


sub showHTML {
  $template->parse(main => "main");
  return $template->fetch("main");
}

sub loadBook {
  my ( $isbn ) = @_;
  my ( $return );

  $isbn =~ s/[^0-9X]//g;
  if (length($isbn) == 10 || length($isbn) == 13)
  {
    my ($select);
    $return = "<TABLE BORDER='0'>";

    my ($imgsrc, $booktitle, $bookauthors, $bookinfo) = getGoogleBookInfo($isbn);

    $return .= qq|
<TR>
<TD VALIGN="top"><P><IMG SRC="$imgsrc"></P></TD>
<TD VALIGN="top"><H2>$booktitle</H2><P>$bookauthors<BR>$bookinfo</P></TD>
</TR>|;

    $return .= "</TABLE>\n";
  }
  else
  { $return = "<P><FONT color='red'>ISBN numbers are 10 or 13 characters long.</FONT></P>"; }

  return $return;
}
