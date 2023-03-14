#   Package of miscellaneous processing functions
#   
#  2013-11-16 by TAKENAKA, A.
#  rev 2020-07-07  by OGAWA, Yui
#  

package Util;

use Exporter;
# use CGI::Carp('fatalsToBrowser');

use Encode;
use HTML::Template;
use Time::Piece;

use Info;

@ISA = qw(Exporter);

@EXPORT = qw(

form_str_utf8
html_escape
quote_escape
inequ_escape
inequ_restore
get_day_date_time
load_html_tmpl
write_login_log
);

use strict;
use utf8;

my $t = localtime;


##########################
# Return the value corresponding to the key from the CGI object.
# Restore double quotes and convert < and > to &lt;, &gt; to make use of them as valid tags.

# Return value can be displayed as HTML.
#
#  form_str_utf8(CGI_object, Key)

sub form_str_utf8
{
    my ($cgi, $key) = @_;

    my $limit_len = 4096; # If the input is longer than this, it is considered abnormal and terminated.

    my $str = $cgi->param($key);
    return '' if not defined $str;  # If there is no data with this name, an empty string is returned.

    $str  = &Encode::decode('utf8', $str);
    $str =~ s/(\x0D\x0A|\x0D|\x0A)/\n/g;  # Absorb differences in line feed codes

    # $str = &inequ_escape($str);
    # $str = &quote_escape($str);
    
    $str = $cgi->escapeHTML($str);
	
    #$str =~ s/&#34;/\"/g;  
    # $str = &html_escape($str);

    return $str;
}


######################################

sub html_escape
{
    my $str = shift @_;

    $str =~ s/</&lt;/g;    # From inequality sign to &.
    $str =~ s/>/&gt;/g;

    return $str;
}


#######################################

sub quote_escape
{
    my $str = shift @_;
    $str =~ s/\"/&#34;/g;
    return $str;
}

sub quote_restore
{
    my $str = shift @_;
    $str =~ s/&#34;/\"/g;
    return $str;
}

#######################################

sub inequ_escape
{
    my $str = shift @_;
    $str =~ s/</&lt;/g;
    $str =~ s/>/&gt;/g;
    return $str;
}

sub inequ_restore
{
    my $str = shift @_;
    $str =~ s/&lt;/</g;
    $str =~ s/&gt;/>/g;
    return $str;
}


#####################################

sub get_day_date_time 
{
	my $day = $t->strftime('%Y/%m/%d');
	my $date = $t->strftime('%Y/%m/%d %H:%M:%S');
	my $time = time; #unix time
	return ($day, $date, $time);
}

#####################################
#  Generate and return an HTML::Template object.

sub load_html_tmpl
{
    my $tmpl_file = shift @_;

    my $code = 'utf8';

    my $template_path = &Info::get_template_path();

    open (my $fh, ('<:' . $code), ($template_path . $tmpl_file) )
                   || die ("Failed to open $template_path$tmpl_file");
                   
    my $tmpl = HTML::Template->new( filehandle => $fh );
    close $fh;

    return $tmpl;
}


######################################
# 

sub write_login_log
{
	my $user = shift @_;
	my $login = shift @_; #login or dlogin
	my ($day, $date, $time) = &get_day_date_time;
	my $login_log_file;
	
	if ($login eq "login"){
		$login_log_file = &Info::get_login_log_path;
    }
    else{ #dlogin
    	$login_log_file = &Info::get_d_login_log_path;
    }
    open (FILE, ">>", $login_log_file) or die "Failed to open $login_log_file\n";
    
    print FILE &Encode::encode('utf-8', "$date\t$time\t$ENV{REMOTE_ADDR}\t$ENV{HTTP_USER_AGENT}\t$user\n"); 
    close (FILE); 
}
1;
