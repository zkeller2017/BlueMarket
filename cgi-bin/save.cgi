#!/usr/bin/perl

require "common.pl";

# -----------------------------------------------

if ($session->param("_IS_LOGGED_IN"))
{
  my ($adNum) = $cgi->param('recnum');
  my ($adUsername) = $session->param('username');
  my ($adStatus) = $cgi->param('status');
  my ($adCourse) = $cgi->param('course');
  my ($adISBN) = $cgi->param('isbn'); $adISBN =~ s/[^0-9X]//g;
  my ($adCondition) = $cgi->param('condition');
  my ($adComments) = $cgi->param('comments');

  if ($adNum eq 'NEW')
  {
     $insert = $dbh->prepare("INSERT into Ads
	(AdUsername, AdStatus, AdCourse,
	 AdISBN, AdCondition, AdComments)
	values (?, ?, ?, ?, ?, ?)");
     $insert->execute($adUsername . '', $adStatus . '', $adCourse . '',
	 $adISBN . '', $adCondition . '', $adComments . '');
     $insert->finish();
  }
  else
  {
     $update = $dbh->prepare("UPDATE Ads
	SET AdISBN=?, AdCondition=?, AdStatus=?, AdComments=?
	WHERE AdNum=? AND AdUsername=?");
     $update->execute(
	$adISBN, $adCondition, $adStatus, $adComments,
	$adNum, $session->param('username'));
  }

  $redirect = "main.cgi";
  print $cgi->redirect(-cookie=>$cookie, -uri=>$redirect );
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
