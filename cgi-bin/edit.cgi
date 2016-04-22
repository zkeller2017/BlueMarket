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

  my $select = $dbh->prepare("
    SELECT AdStatus, AdCourse, AdISBN, AdCondition, AdComments
    FROM Ads WHERE AdNum = ? and AdUsername = ?");
  $select->execute($cgi->param('id'), $session->param('username'));
  $select->bind_columns( undef,
	\$adStatus, \$adCourse, \$adISBN, \$adCondition, \$adComments );
  $select->fetch;

  my ($course) = lookupCourse($adCourse);

  $template->define(main => "entry.html");
  $template->assign(CONTENTS => $contents);
  $template->assign(FIRSTNAME => uc($fname));
  $template->assign(LASTNAME => uc($lname));
  $template->assign(COURSE => $course);
  $template->assign(COURSENUM => $adCourse);
  $template->assign(RECNUM => $cgi->param('id'));
  $template->assign(ISBN => $adISBN);
  $template->assign(CONDITION => $adCondition);
  $template->assign(COMMENTS => $adComments);

  if ($adStatus eq 'A') 
  { $template->assign(STATUSA => 'CHECKED'); }
  else { $template->assign(STATUSA => ''); }
  if ($adStatus eq 'I') 
  { $template->assign(STATUSI => 'CHECKED'); }
  else { $template->assign(STATUSI => ''); }
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
