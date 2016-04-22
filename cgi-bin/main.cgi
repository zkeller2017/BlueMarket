#!/usr/bin/perl

require "common.pl";

use CGI::Ajax;
my $ajax = CGI::Ajax->new(
	loadDept => \&loadDept,
	loadCourse => \&loadCourse
);

# -----------------------------------------------

if ($session->param("_IS_LOGGED_IN"))
{
#  print $cgi->header(-cookie=>$cookie );
  my $depts;

  my $select = $dbh->prepare("SELECT CourseDept FROM `Courses` GROUP BY CourseDept;");
  $select->execute();
  while (my @data = $select->fetchrow_array())
  { $depts .= qq|<option value="$data[0]">$data[0]</option>\n|; }
  $select->finish();

  $contents = qq|
<FORM ACTION="$cgiurl/view.cgi" METHOD="POST" NAME="main" accept-charset=utf-8>
<h2>Select department & course:</h2>
<P><select name="dept" id="dept">
<option value="" selected></option>
$depts
<option value=""></option>
</select>

<select name="COURSE" id="course"/>
<option value="" selected></option>
</select></p>
<p id="ads"></p>
|;

  $contents .= "</FORM>\n";

  $template->define(main => "main.html");
  $template->assign(CONTENTS => $contents);
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

sub loadDept {
    my ( $dept ) = @_;
    my $select = $dbh->prepare("select CourseNum, CourseName
        from Courses where CourseDept=? order by CourseName");
    $select->execute($dept);
    my $return = '<option value="" selected></option>';
    while (my @data = $select->fetchrow_array())
    { $return .= qq|<option value="$data[0]">$data[1]</option>\n|; }
    $select->finish();
    return $return;
}

sub loadCourse {
    my ( $course ) = @_;
    my ($select, $return);
    $return = "<TABLE BORDER='0'>";

    $select = $dbh->prepare("
	select AdNum, AdUsername, AdISBN, AdCondition, AdComments
        from Ads where AdCourse=? and AdStatus='A'
	order by AdNum");
    $select->execute("$course");
    $select->bind_columns( \( @row{ @{$select->{NAME_lc} } } ));
    while ($select->fetch)
    {
    my ($lname, $fname) = lookupStudent($row{'adusername'});
    my ($imgsrc, $booktitle, $bookauthors, $bookinfo) = getGoogleBookInfo($row{'adisbn'});

    $return .= qq|
<TR>
<TD VALIGN="top"><P><IMG SRC="$imgsrc">|;

    if ($row{'adusername'} eq $session->param('username'))
    { $return .= qq|<BR><A HREF="$cgiurl/edit.cgi?id=$row{'adnum'}">Edit listing</A>|; }

    $return .= qq|</P></TD>
<TD VALIGN="top"><H2>$booktitle</H2><P>$bookauthors<BR>$bookinfo</P>
<P><EM>Interested in this book? E-mail <A HREF="mailto:$row{'adusername'}\@pingry.org">$fname $lname</A></EM><BR>
$row{'adcomments'} (Condition: $row{'adcondition'}/10)</P>
</TD>
</TR>|;
}
    $select->finish();
  $return .= "</TABLE>\n";
  $return .= qq|<P><input type="submit" name="add" value="Add New Listing"/ onClick="this.form.action='/cgi-bin/bookexchange/new.cgi'"></P>|;

    return $return;
}
