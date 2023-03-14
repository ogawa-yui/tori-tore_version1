#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Quiz Method Explanation Screen
#
#   2020-08-05 by OGAWA, Y.

use lib qw(pm .);

use strict;
use warnings;
use utf8;

use CGI;
use HTML::Template;
use CGI::Carp( 'fatalsToBrowser' );
use Time::Piece;

use Info;
use Util;
use Quiz;
use Par;

my $q = CGI->new;
$q->charset( 'UTF-8' );

# If you came to this page without logging in
unless ($q->param( 'user' )){  # No user name → Not logged in
	# Display message and exit
	my $tmpl = &Util::load_html_tmpl('not_logged_in_message.tmpl' );
	print $q->header;
	print &Encode::encode('utf-8', $tmpl->output);
	exit; # Terminate all programs
}

my $tmpl = &Util::load_html_tmpl('09_quiz_guide.tmpl' );

my $user = &Util::form_str_utf8($q, 'user' );
$tmpl->param( user => "$user" ); 


my ($day, $date, $time) = &Util::get_day_date_time;

$tmpl->param( n_quizzes_per_day => $Par::N_QUIZZES_PER_DAY );

print $q->header;
print &Encode::encode('utf-8', $tmpl->output);
