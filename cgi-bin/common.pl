#!/usr/bin/perl

# -----------------------------------------------
# Define variables here

# Path where the HTML templates are stored
$templatedir = '/path/to/templates/';

# URL where the CGI scripts are stored
$cgiurl = 'https://www.pingry.org/cgi-bin/bookexchange';

# Database
$DBSVR  = 'server.pingry.org';
$DBNAME = 'database';
$DBUSER = 'username';
$DBPASS = 'password';

# -----------------------------------------------
# Setup usage of modules

use CGI qw(:standard); 
use CGI::Session qw/-ip-match/;
use CGI::FastTemplate;

use File::Spec;

use Business::ISBN;
use DBI;
use JSON;
use LWP;
use Mail::Sendmail;
use Switch;

# -----------------------------------------------
# Main body of code

$cgi = new CGI;
$session = new CGI::Session(undef, $cgi, {Directory=>File::Spec->tmpdir});
$template = new CGI::FastTemplate("$templatedir");

$session->expire('+1h');
$session->save_param($cgi);

$cookie = $cgi->cookie(CGISESSID => $session->id);

$dsn = "DBI:mysql:$DBNAME:$DBSVR";
$dbh = DBI->connect($dsn, $DBUSER, $DBPASS) or die ("Cannot connect");


# -----------------------------------------------
# Subroutines

sub lookupStudent {
  my ($student) = @_;
  my ($lastname, $firstname);

  $select = $dbh->prepare("select lastname, firstname
      from Students where username=?");
  $select->execute($student);
  @data = $select->fetchrow_array();
  $select->finish();

  $lastname = $data[0];
  $firstname = $data[1];

  return ($lastname, $firstname);
}

sub lookupCourse {
  my ($courseNum) = @_;
  my ($CourseName);

  $select = $dbh->prepare("select CourseName
      from Courses where CourseNum=?");
  $select->execute($courseNum);
  @data = $select->fetchrow_array();
  $select->finish();

  return ($data[0]);
}

sub dateToday {
  my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
    localtime(time);

  $year += 1900;

  my @month = qw(
	January February March
	April May June
	July August September
	October November December
  );

  my @dayofweek = qw(
	Sunday Monday Tuesday Wednesday Thursday Friday Saturday
  );

  $humandate = "$dayofweek[$wday], $month[$mon] $mday, $year";

  $mon++;  if ($mon < 10) { $mon = "0$mon"; }
  if ($mday < 10) { $mday = "0$mday"; }
  $sqldate = join('-', $year, $mon, $mday);

  return ($humandate, $sqldate);
}


sub shortDate
{
  my ($date) = @_;
  ($year, $month, $day) = split(/-/, $date);
  $month =~ s/^0//;
  $day =~ s/^0//;

  return "$month/$day";
}


sub dateFromSQL {
  my ($sqldate) = @_;
  my ($year, $mon, $day) = split(/-/, $sqldate);
  $mon--;

  my @month = qw(
	January February March
	April May June
	July August September
	October November December
  );

  $humandate = "$month[$mon] $day, $year";

  return ($humandate);
}



sub getGoogleBookInfo
{
  my ($userISBN) = @_;
  $userISBN =~ s/[^0-9X]//g;
  $checkISBN = Business::ISBN->new( $userISBN );

  if (length($userISBN) == 10 || length($userISBN) == 13)
  {
    if ($checkISBN->is_valid())
    {
      my $isbn = $checkISBN->as_string([]);

      # Get data
      my $ua = LWP::UserAgent->new;
      my $req = HTTP::Request->new(
        GET => "https://www.googleapis.com/books/v1/volumes?q=isbn:$isbn" );
      my $res = $ua->request( $req );

      # read JSON data
      my $data = decode_json($res->content);
      my @authors = @{ $data->{'items'}[0]{'volumeInfo'}{'authors'} };

      my $imgsrc = $data->{'items'}[0]{'volumeInfo'}{'imageLinks'}{'thumbnail'};
      $imgsrc =~ s/^http/https/;

      my $booktitle = $data->{'items'}[0]{'volumeInfo'}{'title'};
      my $bookauthors = join(', ', @authors);
      my $bookinfo = "Pub. $data->{'items'}[0]{'volumeInfo'}{'publishedDate'}
        by $data->{'items'}[0]{'volumeInfo'}{'publisher'}";

      return $imgsrc, $booktitle, $bookauthors, $bookinfo;
      exit;
    }
    else
    {
      $imgsrc = '/ExampleISBN.png';
      $booktitle = "$userISBN is not a valid ISBN";
      $bookauthors = 'Please check the number entered.';
      $bookinfo = '';

      return $imgsrc, $booktitle, $bookauthors, $bookinfo;
    }
  }
  else
  {
    $imgsrc = '/blank.png';
    $booktitle = "$userISBN";
    $bookauthors = '';
    $bookinfo = '';

    return $imgsrc, $booktitle, $bookauthors, $bookinfo;
  }  
}
