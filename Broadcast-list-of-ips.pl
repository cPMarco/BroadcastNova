#!/usr/bin/perl
use strict;
use warnings;

use Getopt::Long;
use File::Basename;
use FindBin qw($Bin);

#<<<
Getopt::Long::GetOptions(
    \my %opt,
    'input_file=s',
    'all_vms|a',
    'sandbox_vms|s',
    'binary_vms|b',
    'idev_vms|i',
    'verbose|v',
    'help|h',
    'man',
) or die('[error] Use -h for help');
#>>>

# If I'm gona redo all that prunning again, here's the start
# nova list --fields 'name','created','status','networks','metadata'
my $FILE        = $opt{'file'} // "$ENV{'HOME'}/.config/broadcastnova/input-servers.txt";
my $TEMP_FILE   = "/tmp/BroadcastNova-IPs.txt";
my $USERNAME    = 'root';
my $SCRIPT_NAME = File::Basename::basename($0);

sub usage() {
    (
        my $help_txt = qq{
        Usage:\n  $SCRIPT_NAME [-h|-a|-s|-b|-i|-v] ( [-f <filepath>] )

        Optional Options:
        -h This help
        -v Cause $SCRIPT_NAME to be verbose
        -f Use custom file for input.  Default is:
            ${FILE}

        Required Options (only one):
        -a SSH into all VM's
        -s SSH into only sandbox VM's
        -b SSH into only binary VM's
        -i SSH into only idev VM's

        }
    ) =~ s/^ {8}//mg;
    print $help_txt;

    exit(1);
}

Pod::Usage::pod2usage( -exitval => 0, -verbose => 2, noperldoc => 1 ) if ( $opt{'man'} );
usage()                                                               if ( $opt{'help'} );

sub print_out {
    my ($text) = @_;
    print "$text\n" if $opt{'verbose'};
}

# Main
print_out "\nFILE: [$FILE]";

# Check for Default Arguments (Instance Name);
unless ( -r $FILE ) {
    print -e "\n[error] FILE not found: $FILE";
    print "[error] Ensure the directory and file exist.";
    usage();
}

my @lines = get_lines($FILE);
validate_num_lines(@lines);

my @ips;
if ( $opt{'all_vms'} ) {
    @ips = get_ips( lines => \@lines, exclude => 'store|manage|verify|tickets' );
}
elsif ( $opt{'sandbox_vms'} ) {
    @ips = get_ips( lines => \@lines, include => 'sand|sb-' );
}
elsif ( $opt{'binary_vms'} ) {
    @ips = get_ips( lines => \@lines, exclude => 'sand|sb-|_sb_|store|manage|verify|tickets' );
}
elsif ( $opt{'idev_vms'} ) {
    @ips = get_ips( lines => \@lines, include => 'store|manage|verify|tickets' );
}
else {
    print -e "\n[error] type of VM is required but was not found.\n";
    usage();
}

print "\nHost IP's found:\n";
print "$_\n" for @ips;

# Check with user to ensure not connecting to wrong servers;
print "\nProceed? Type 'y' for yes\n";
print "[no] ";
my $proceed_ans = <STDIN>;
if ( $proceed_ans !~ /^(y|yes|Y|YES)$/ ) {
    print_out("\nExiting...\n");
    exit(1);
}

# Check if Instances Exist;
my $count = scalar @ips;
if ( $count =~ /^0?$/ ) {
    print "IP(s) Not Found!";
    exit(0);
}

# Determine Row / Column Layout;
my $rows;
if ( $count > 3 ) {
    $rows = sprintf "%.0f", sqrt($count);
}
else {
    $rows = $count;
}

my $ips = join( ' ', @ips );

print "\nRunning:\n";
print "$Bin/scripts/osascript.sh -o $ips -r $rows -u $USERNAME\n\n";
`$Bin/scripts/osascript.sh -o "$ips" -r $rows -u $USERNAME`;

# Subroutines
sub get_lines {
    my $file = shift;
    open( my $fh, '<', $file ) or die "Couldnt open file [$file]: $!";
    chomp( my @lines = <$fh> );
    close $fh;
    return @lines;
}

sub validate_num_lines {
    my @lines = @_;

    my $length_input_file = scalar @lines;
    my $lines_with_ips    = scalar( get_lines_with_ips(@lines) );

    if ( $length_input_file != $lines_with_ips ) {
        print -e "\n[error] Input file needs to be a list full of only servers with IP addresses. Each line is checked.\n";
        usage();
    }
}

sub get_lines_with_ips {
    my @lines          = @_;
    my @lines_with_ips = grep { /(\d{1,3}\.){3}\d{1,3}/ } @lines;
    return @lines_with_ips;
}

sub get_ips {
    my (%args) = @_;

    my $include = ( defined $args{'include'} ) ? qr/$args{'include'}/ : qr/.*/;
    my $exclude = ( defined $args{'exclude'} ) ? qr/$args{'exclude'}/ : qr/^$/;

    return map { s/.+?((\d{1,3}\.){3}\d{1,3}).*/$1/r }
      grep     { /$include/ }
      grep     { !/$exclude/ } @{ $args{'lines'} };
}

exit(1);

# Credit
# https://github.com/ramannanda/Broadcast
# https://github.com/bikboy/Tim/wiki/AWS-CLI----ITerm2-automation-(Mac)
# https://starkandwayne.com/blog/bash-for-loop-over-json-array-using-jq/
# https://alvinalexander.com/source-code/mac-os-x/how-run-multiline-applescript-script-unix-shell-script-osascript
