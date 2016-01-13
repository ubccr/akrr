#!/usr/bin/perl

use strict;
use warnings;
use Inca::Reporter::Performance;
use POSIX qw(strtod);

sub trim($) {
    my $string = shift;
    $string =~ s/^\s+//;
    $string =~ s/\s+$//;
    return $string;
}

my $reporter = new Inca::Reporter::Performance(
    name             => 'xdmod.app.md.namd',
    version          => 1,
    description      => "NAMD: Scalable Molecular Dynamics Package",
    url              => 'http://www.ks.uiuc.edu/Research/namd/',
    measurement_name => 'NAMD'
);

# read and parse arguments
$reporter->addArg( 'bin_path', 'path to the run script' );
$reporter->processArgv(@ARGV);

# the 'run' script is hard-coded
my $exe = $reporter->argValue('bin_path') . "/namd/run";

if ( !-f $exe || !-x $exe ) {
    $reporter->failPrintAndExit("$exe is not found or is not an executable");
}

if ( !exists $ENV{"INCA_BATCHWRAPPER_CORES"} ) {
    $reporter->failPrintAndExit("INCA_BATCHWRAPPER_CORES environmental variable is not set");
}

my $output = $reporter->loggedCommand2("$exe input01");

# write the output to a file, for debugging purpose
my $rawoutputpath = $ENV{INSTALL_DIR} . "/tmp/";
if ( !-d $rawoutputpath ) {
    mkdir $rawoutputpath;
    chmod 0755, $rawoutputpath;
}
my $numCores = $ENV{"INCA_BATCHWRAPPER_CORES"};
if ( open( OUT, ">", $rawoutputpath = $rawoutputpath . $reporter->getName() . ".$numCores.raw_output" ) ) {
    print OUT $output;
    close OUT;
    chmod 0644, $rawoutputpath;
}

#
## Uncomment the following code stanza if you want to debug
#my $holdTerminator = $/;
#undef $/;
#open(IN, "namd_res");
#my $output = <IN>;
#$/ = $holdTerminator;

my $benchmark = $reporter->addNewBenchmark("NAMD");
my $successfulRun;
my $ExeBinSignature;
my @lines = split( $/, $output );

for ( my $j = 0 ; $j <= $#lines ; ++$j ) {
    if ( $lines[$j] =~ /===ExeBinSignature===(.+)/ ) {
        $ExeBinSignature .= trim($1) . "\n";
        next;
    }

    if ( $lines[$j] =~ /^Info: NAMD ([0-9a-zA-Z\.]+)/ ) {
        $benchmark->setParameter( "App:Version", $1 );
        next;
    }

    if ( $lines[$j] =~ /^Info: TIMESTEP\s+([0-9\.]+)/ ) {
        $benchmark->setParameter( "Input:Timestep", $1 . "e-15", "Second per Step" );
        next;
    }

    if ( $lines[$j] =~ /^Info: NUMBER OF STEPS\s+([0-9\.]+)/ ) {
        $benchmark->setParameter( "Input:Number of Steps", $1 );
        next;
    }

    if ( $lines[$j] =~ /^Info: COORDINATE PDB\s+(.+)/ ) {
        $benchmark->setParameter( "Input:Coordinate File", trim($1) );
        next;
    }

    if ( $lines[$j] =~ /^Info: STRUCTURE FILE\s+(.+)/ ) {
        $benchmark->setParameter( "Input:Structure File", trim($1) );
        next;
    }

    if ( $lines[$j] =~ /^Info: STRUCTURE SUMMARY/ ) {
        ++$j;
        for ( my $k = 0 ; $k < 25 ; ++$k, ++$j ) {
            last if ( $lines[$j] =~ /^Info: \*\*\*\*\*/ );
            if ( $lines[$j] =~ /^Info:\s+([0-9]+)\s+ATOMS/ ) {
                $benchmark->setParameter( "Input:Number of Atoms", $1 );
                next;
            }
            if ( $lines[$j] =~ /^Info:\s+([0-9]+)\s+BONDS/ ) {
                $benchmark->setParameter( "Input:Number of Bonds", $1 );
                next;
            }
            if ( $lines[$j] =~ /^Info:\s+([0-9]+)\s+ANGLES/ ) {
                $benchmark->setParameter( "Input:Number of Angles", $1 );
                next;
            }
            if ( $lines[$j] =~ /^Info:\s+([0-9]+)\s+DIHEDRALS/ ) {
                $benchmark->setParameter( "Input:Number of Dihedrals", $1 );
                next;
            }
        }
        next;
    }

    if ( $lines[$j] =~ /Info: Benchmark time:/ ) {
        my @tokens = split( /[:\s]+/, $lines[$j] );
        for ( my $k = 3 ; $k < $#tokens ; ++$k ) {
            if ( "days/ns" eq $tokens[$k] ) {
                $benchmark->setStatistic( "Molecular Dynamics Simulation Performance", 1.0 / $tokens[ $k - 1 ] . "e-9", "Second per Day" );
                last;
            }
        }
        next;
    }

    if ( $lines[$j] =~ /^WallClock:\s+([0-9\.]+)\s+CPUTime:\s+([0-9\.]+)\s+Memory:\s+([0-9\.]+)/ ) {
        $benchmark->setStatistic( "Wall Clock Time", $1, "Second" );

        #$benchmark->setStatistic("User Time", $2, "Second");
        $benchmark->setStatistic( "Memory", $3, "MByte" );
        $successfulRun = 1;
        next;
    }

    if ( $lines[$j] =~ /^End of program/ ) {
        $successfulRun = 1;
        next;
    }

}

$reporter->failPrintAndExit("$output") unless ( defined($successfulRun) );
$benchmark->setParameter( "App:ExeBinSignature", `echo "$ExeBinSignature"|gzip -9|base64 -w 0` ) if ( defined($ExeBinSignature) );
$benchmark->setParameter( "RunEnv:Nodes",        $ENV{"INCA_BATCHWRAPPER_NODELIST"} )            if ( exists $ENV{"INCA_BATCHWRAPPER_NODELIST"} );
$reporter->setResult(1);
$reporter->print();
