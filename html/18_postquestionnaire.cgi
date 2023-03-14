#!/usr/bin/perl --
#!c:/perl64/bin/perl.exe

#
#   Post-questionnaire screen
#
#   2020-08-05 by OGAWA, Y.

use lib qw(pm .);


use strict;
use warnings;
use CGI;
use HTML::Template;
use CGI::Carp( 'fatalsToBrowser' );
use Time::Piece;

use Util;

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


my $user = &Util::form_str_utf8($q, 'user' ); 


my $tmpl = &Util::load_html_tmpl('18_postquestionnaire.tmpl' );
$tmpl->param( user => "$user" ); 


print $q->header;
print &Encode::encode('utf-8', $tmpl->output);

